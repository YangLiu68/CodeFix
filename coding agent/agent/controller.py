import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

from tools.read_file import read_file
from tools.write_file import write_file
from tools.search_code import search_code
from tools.run_command import run_command
from context.repo_map import RepoMap
from editing.patch_parser import PatchParser
from editing.patch_apply import apply_patch


# ─── OpenAI function-calling schema for each tool ───────────────────
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the full contents of a file. Use this to inspect code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Relative path from project root"}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or overwrite a file with given content. ALWAYS use this to save code to disk instead of showing code in the chat.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "content":   {"type": "string"}
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_code",
            "description": "Search for a string pattern across all source files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "path":  {"type": "string", "description": "Directory to search. Use '.' for project root."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a shell command and return stdout/stderr. Use to run Python files, tests, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "apply_patch",
            "description": "Replace an exact block of text in a file with new text. Use this to fix bugs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path":    {"type": "string"},
                    "search_text":  {"type": "string", "description": "Exact text to find (must exist in file)"},
                    "replace_text": {"type": "string", "description": "New text to replace it with"}
                },
                "required": ["file_path", "search_text", "replace_text"]
            }
        }
    }
]


class AgentController:
    def __init__(self, model: str = None):
        self.repo_map = RepoMap()
        self.client = None
        self.history = []   # Persistent conversation memory

        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        # Priority: explicit arg > env var > default
        self.model = model or os.getenv("MODEL_NAME") or "gpt-4o-mini"

        if api_key:
            if base_url:
                # Support custom endpoints like Z.AI or local LLMs
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=base_url
                )
            elif api_key.startswith("sk-or-"):
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
            else:
                self.client = OpenAI(api_key=api_key)

        self.tool_registry = {
            "read_file":   read_file,
            "write_file":  write_file,
            "search_code": lambda query, path=".": search_code(query, path),
            "run_command": run_command,
            "apply_patch": apply_patch,
        }

    # ─────────────────────────────────────────────────────────────────
    def get_system_prompt(self):
        return (
            "You are a senior software engineer CLI Agent. Your working directory is the project root.\n"
            f"Project structure:\n{self.repo_map.get_summary()}\n\n"
            "Tools: read_file, write_file, search_code, run_command, apply_patch.\n\n"
            "MANDATORY RULES:\n"
            "1. BUG CHECK: Do NOT rely solely on `py_compile`. ALWAYS execute the file or its associated unit tests using `run_command` "
            "to catch runtime errors (e.g., NameErrors, ImportErrors).\n"
            "2. GUI/GAME BUGS (pygame, tkinter, etc): You CANNOT see the graphical window. "
            "To debug runtime bugs in GUI apps, use this strategy:\n"
            "   a) Use read_file to read the current source code carefully.\n"
            "   b) Inject a crash logger using apply_patch: wrap the main entry point in "
            "try/except and write errors + traceback to 'crash.log'. Example:\n"
            "      import traceback\n"
            "      try:\n"
            "          gameLoop()\n"
            "      except Exception as e:\n"
            "          open('crash.log','w').write(traceback.format_exc())\n"
            "   c) Use run_command to run the game with a timeout: `timeout 3 python3 snake_game.py || true`\n"
            "   d) Use read_file('crash.log') to read the error.\n"
            "   e) Fix the bug with apply_patch, then repeat.\n"
            "3. BEFORE PATCHING: Always call read_file on the target file right before apply_patch. "
            "Use the EXACT text currently in the file.\n"
            "4. AFTER PATCHING: If apply_patch returns ERROR, call read_file again and retry.\n"
            "5. WRITE CODE: Always use write_file to save files. Never paste code only in chat.\n"
            "6. VERIFY: After fixing, run the file or py_compile it to confirm.\n"
            "7. SUMMARY: Report what bug was found, what was fixed, and the final status."
        )
    # ─────────────────────────────────────────────────────────────────
    def _dispatch_tool(self, name: str, arguments: dict) -> str:
        fn = self.tool_registry.get(name)
        if fn is None:
            return f"Error: unknown tool '{name}'"
        try:
            result = fn(**arguments)
            return str(result) if result is not None else "(no output)"
        except Exception as e:
            return f"Tool error: {e}"

    # ─────────────────────────────────────────────────────────────────
    def _agent_loop(self):
        """
        Core agentic loop with STREAMING text output and real tool execution.
        Yields string chunks to the CLI.
        """
        messages = (
            [{"role": "system", "content": self.get_system_prompt()}]
            + self.history
        )

        MAX_TOOL_ROUNDS = 10
        for _ in range(MAX_TOOL_ROUNDS):

            # ── streaming API call ───────────────────────────────────
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                stream=True,
            )

            # Accumulate streaming chunks
            text_content = ""
            tool_calls_raw = {}  # index → {id, name, args_str}
            finish_reason = None

            for chunk in stream:
                choice = chunk.choices[0]
                finish_reason = choice.finish_reason
                delta = choice.delta

                # ── streaming text ───────────────────────────────────
                if delta.content:
                    text_content += delta.content
                    yield delta.content   # ← real-time streaming to terminal

                # ── accumulate tool call deltas ──────────────────────
                if delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        idx = tc_delta.index
                        if idx not in tool_calls_raw:
                            tool_calls_raw[idx] = {
                                "id": tc_delta.id or "",
                                "name": tc_delta.function.name or "",
                                "args_str": ""
                            }
                        if tc_delta.id:
                            tool_calls_raw[idx]["id"] = tc_delta.id
                        if tc_delta.function.name:
                            tool_calls_raw[idx]["name"] = tc_delta.function.name
                        if tc_delta.function.arguments:
                            tool_calls_raw[idx]["args_str"] += tc_delta.function.arguments

            # ── final text reply → done ──────────────────────────────
            if finish_reason == "stop" or not tool_calls_raw:
                if text_content:
                    self.history.append({"role": "assistant", "content": text_content})
                return

            # ── execute tool calls ───────────────────────────────────
            # Add assistant message with tool_calls to history
            tool_calls_list = []
            for idx in sorted(tool_calls_raw.keys()):
                tc = tool_calls_raw[idx]
                tool_calls_list.append({
                    "id": tc["id"],
                    "type": "function",
                    "function": {"name": tc["name"], "arguments": tc["args_str"]}
                })

            messages.append({
                "role": "assistant",
                "content": text_content or None,
                "tool_calls": tool_calls_list
            })
            self.history.append({
                "role": "assistant",
                "content": text_content or None,
                "tool_calls": tool_calls_list
            })

            for tc in tool_calls_list:
                fn_name = tc["function"]["name"]
                try:
                    fn_args = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    fn_args = {}

                # Pretty-print the tool call
                args_display = ", ".join(
                    f"{k}={repr(v)[:80]}" for k, v in fn_args.items()
                )
                yield f"\n🔧 **{fn_name}**({args_display})\n"

                result = self._dispatch_tool(fn_name, fn_args)

                # Truncate very long results for display
                display_result = result if len(result) < 2000 else result[:2000] + "\n...(truncated)"
                yield f"```\n{display_result}\n```\n"

                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                }
                messages.append(tool_msg)
                self.history.append(tool_msg)

        yield "\n⚠️ Reached max tool-call rounds."

    # ─────────────────────────────────────────────────────────────────
    def process_query(self, query: str):
        if not self.client:
            yield "⚠️  OPENAI_API_KEY not set. Please edit `.env`.\n"
            return

        # Slash commands
        if query.strip() == "/map":
            yield f"```text\n{self.repo_map.get_summary()}\n```"
            return

        if query.strip() == "/clear":
            self.history.clear()
            yield "🧹 Conversation cleared.\n"
            return

        if query.startswith("/fix "):
            parts = query[5:].split(" --test ")
            if len(parts) < 2:
                yield "Usage: `/fix [task] --test [command]`\n"
                return
            yield from self._autonomous_fix(parts[0].strip(), parts[1].strip())
            return

        self.history.append({"role": "user", "content": query})
        yield from self._agent_loop()

    # ─────────────────────────────────────────────────────────────────
    def _autonomous_fix(self, task: str, test_command: str, max_retries: int = 3):
        prompt = (
            f"Task: {task}\n"
            f"After fixing, run `{test_command}` to verify. Keep fixing until it passes."
        )
        self.history.append({"role": "user", "content": prompt})

        for attempt in range(max_retries):
            yield f"\n🔁 **Attempt {attempt + 1}/{max_retries}**\n"
            yield from self._agent_loop()

            yield f"\n🧪 Running `{test_command}`...\n"
            result = run_command(test_command)

            if "error" not in result.lower() and "traceback" not in result.lower():
                yield f"✅ **Passed!**\n```\n{result}\n```"
                return

            yield f"❌ **Failed**\n```\n{result[:800]}\n```\n"
            self.history.append({
                "role": "user",
                "content": f"Still failing:\n{result}\nFix it."
            })

        yield "🏁 Max retries reached."
