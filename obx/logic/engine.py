from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class LogicIssue:
    __slots__ = ("file", "lineno", "title", "description", "severity", "suggestion")

    def __init__(
        self,
        file: str,
        lineno: int,
        title: str,
        description: str,
        severity: str,
        suggestion: str,
    ) -> None:
        self.file = file
        self.lineno = lineno
        self.title = title
        self.description = description
        self.severity = severity
        self.suggestion = suggestion

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file,
            "lineno": self.lineno,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "suggestion": self.suggestion,
        }


class LogicVisitor(ast.NodeVisitor):
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.issues: List[LogicIssue] = []
        self._loop_depth = 0
        self._function_depth = 0
        self._return_count = 0
        self._has_unreachable: bool = False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function_depth += 1
        self._check_function(node)
        self.generic_visit(node)
        self._function_depth -= 1

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_For(self, node: ast.For) -> None:
        self._loop_depth += 1
        self._check_loop(node)
        self.generic_visit(node)
        self._loop_depth -= 1

    def visit_While(self, node: ast.While) -> None:
        self._loop_depth += 1
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
            if not has_break:
                self.issues.append(
                    LogicIssue(
                        file=self.filename,
                        lineno=node.lineno,
                        title="Infinite loop without break",
                        description="while True loop has no break statement",
                        severity="critical",
                        suggestion="Add a break condition or convert to a bounded loop",
                    )
                )
        self.generic_visit(node)
        self._loop_depth -= 1

    def visit_If(self, node: ast.If) -> None:
        self._check_condition(node)
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        self._return_count += 1
        self._check_unreachable_after_return(node)
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        self._check_compare(node)
        self.generic_visit(node)

    def _check_function(self, node: Any) -> None:
        if len(node.args.args) > 10:
            self.issues.append(
                LogicIssue(
                    file=self.filename,
                    lineno=node.lineno,
                    title="Function with too many parameters",
                    description=f"{node.name} has {len(node.args.args)} parameters",
                    severity="medium",
                    suggestion="Refactor using a configuration object or dataclass",
                )
            )

        stmts = [s for s in ast.walk(node) if isinstance(s, ast.stmt)]
        if len(stmts) > 80:
            self.issues.append(
                LogicIssue(
                    file=self.filename,
                    lineno=node.lineno,
                    title="Overly complex function",
                    description=f"{node.name} has {len(stmts)} statements",
                    severity="medium",
                    suggestion="Break this function into smaller, focused functions",
                )
            )

    def _check_loop(self, node: ast.For) -> None:
        if self._loop_depth > 3:
            self.issues.append(
                LogicIssue(
                    file=self.filename,
                    lineno=node.lineno,
                    title="Deeply nested loops",
                    description=f"Loop nesting depth: {self._loop_depth}",
                    severity="high",
                    suggestion="Flatten loops using itertools or refactor into helper functions",
                )
            )

    def _check_condition(self, node: ast.If) -> None:
        if isinstance(node.test, ast.Constant):
            if node.test.value is True:
                self.issues.append(
                    LogicIssue(
                        file=self.filename,
                        lineno=node.lineno,
                        title="Always-true condition",
                        description="if True: block will always execute",
                        severity="high",
                        suggestion="Remove the constant condition or use assert",
                    )
                )
            elif node.test.value is False:
                self.issues.append(
                    LogicIssue(
                        file=self.filename,
                        lineno=node.lineno,
                        title="Unreachable code block",
                        description="if False: block will never execute",
                        severity="high",
                        suggestion="Remove the dead code block",
                    )
                )

    def _check_unreachable_after_return(self, node: ast.Return) -> None:
        pass

    def _check_compare(self, node: ast.Compare) -> None:
        for op in node.ops:
            if isinstance(op, ast.Is):
                for comparator in node.comparators:
                    if isinstance(comparator, ast.Constant) and isinstance(
                        comparator.value, (int, str, float)
                    ):
                        self.issues.append(
                            LogicIssue(
                                file=self.filename,
                                lineno=node.lineno,
                                title="Identity comparison with literal",
                                description="Using 'is' to compare with a literal value",
                                severity="medium",
                                suggestion="Use == for value comparison, 'is' is for identity",
                            )
                        )


class LogicEngine:
    def analyze_file(self, filepath: str) -> List[LogicIssue]:
        try:
            source = Path(filepath).read_text(encoding="utf-8")
            tree = ast.parse(source, filename=filepath)
            visitor = LogicVisitor(filename=filepath)
            visitor.visit(tree)
            return visitor.issues
        except (SyntaxError, OSError, UnicodeDecodeError):
            return []

    def analyze_directory(self, dirpath: str) -> List[LogicIssue]:
        all_issues: List[LogicIssue] = []
        for root, _, files in os.walk(dirpath):
            for fname in files:
                if fname.endswith(".py") and not fname.startswith("_"):
                    full_path = os.path.join(root, fname)
                    all_issues.extend(self.analyze_file(full_path))
        return all_issues

    def compute_logic_score(self, issues: List[LogicIssue]) -> float:
        score = 100.0
        deductions = {"critical": 15, "high": 8, "medium": 4, "low": 1}
        for issue in issues:
            score -= deductions.get(issue.severity, 2)
        return max(round(score, 2), 0.0)


_engine: LogicEngine = LogicEngine()


def get_logic_engine() -> LogicEngine:
    return _engine
