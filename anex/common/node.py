#!/usr/bin/python3
"""
Extracts metadata from nodes
"""

import os
import ast
__all__ = ['Node']


class MetadataScanner(ast.NodeVisitor):
    def __init__(self):
        self.title = None
        self.inputs = {}
        self.outputs = {}
        self.extrain = False
        self.extraout = False

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            return
        fname = node.func.id
        if fname == 'title':
            # XXX: Should we not take it if we don't recognize the signature?
            t = node.args[0]
            if isinstance(t, ast.Str):
                self.title = t.s
        elif fname in ('input', 'output'):
            if fname == 'input':
                names = self.inputs
                def extra(var):
                    self.extrain |= var
            else:
                names = self.outputs
                def extra(var):
                    self.extraout |= var

            label, typ = node.args[0:2]
            if isinstance(label, ast.Str) and isinstance(typ, ast.Name):
                names[label.s] = typ.id
            elif isinstance(label, ast.Str):  # the type is not a simple name
                names[label.s] = None
            else:  # The name is not a simple string (the type can be anything)
                extra(True)

    def generic_visit(self, node):
        for f in node._fields:
            fv = getattr(node, f)
            if isinstance(fv, ast.AST):
                self.visit(fv)
            elif isinstance(fv, list):
                for n in fv:
                    self.visit(n)


class Node:
    """
    Lazy-loaded node metadata
    """
    USER_DIR = os.path.expanduser('~/.local/share/antimony/nodes')  # FIXME: Linux only

    # XXX: On load, should we just write to __dict__, so it skips the descriptor in future loads?
    def __init__(self, path):
        self.path = path

    _source = None

    @property
    def source(self):
        if self._source is None:
            with open(self.path, 'rU') as nf:
                self._source = nf.read()
            # TODO: Normalize
        return self._source

    _headers = None

    def _parse_headers(self):
        for line in self.source.split('\n'):
            line = line.strip()
            if not line.startswith('#'):
                break
            line = line[1:].lstrip()  # Remove the leading '#' and any whitespace behind it
            if ':' in line:
                k, v = line.split(':', 1)
                yield k.rstrip().upper(), v.lstrip()

    @property
    def headers(self):
        if self._headers is None:
            self._headers = dict(self._parse_headers())
        return self._headers

    _docstring = None
    _title = None
    _inputs = None
    _extrainputs = None
    _outputs = None
    _extraoutputs = None

    def _scan_ast(self):
        tree = ast.parse(self.source)
        self._docstring = ast.get_docstring(tree)

        ms = MetadataScanner()
        ms.visit(tree)  # Populate the variables above
        self._title = ms.title
        self._inputs = ms.inputs
        self._extrainputs = ms.extrain
        self._outputs = ms.outputs
        self._extraoutputs = ms.extraout

    @property
    def docstring(self):
        if self._docstring is None:
            self._scan_ast()
        return self._docstring

    @property
    def title(self):
        if self._title is None:
            self._scan_ast()
        return self._title

    @property
    def inputs(self):
        if self._inputs is None:
            self._scan_ast()
        return self._inputs

    @property
    def extrainputs(self):
        if self._extrainputs is None:
            self._scan_ast()
        return self._extrainputs

    @property
    def outputs(self):
        if self._outputs is None:
            self._scan_ast()
        return self._outputs

    @property
    def extraoutputs(self):
        if self._extraoutputs is None:
            self._scan_ast()
        return self._extraoutputs

    @classmethod
    def list_nodes(cls, dirname):
        for dirpath, _, files in os.walk(dirname):
            for f in files:
                if f.endswith('.node'):
                    yield cls(os.path.join(dirpath, f))

    @classmethod
    def user_nodes(cls):
        yield from cls.list_nodes(cls.USER_DIR)

if __name__ == '__main__':
    for node in Node.user_nodes():
        print(node.path)
        print('\t', node.title)
        print('\t', repr(node.docstring))
        for k, v in node.headers.items():
            print('\t', k, ':', v)
        for attr in ('inputs', 'extrainputs', 'outputs', 'extraoutputs'):
            print('\t', attr, ':', repr(getattr(node, attr)))
