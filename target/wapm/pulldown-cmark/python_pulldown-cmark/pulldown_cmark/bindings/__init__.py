'''
Bindings to the  library.
'''

from pathlib import Path
from typing import Optional, Any

from wasmer import Store, Module, wasi # type: ignore
from .pulldown.bindings import Pulldown as _Pulldown

class Bindings:
    """
    Instantiate bindings to the various libraries in this package.
    """

    def __init__(self, store: Store):
        self._store = store
        self._cache: dict[str, Module] = {}

    def _get_module(self, filename: str) -> Module:
        if filename in self._cache:
            return self._cache[filename]

        wasm = Path(__file__).parent.joinpath(filename).read_bytes()
        module = Module(self._store, wasm)
        self._cache[filename] = module
        return module

    def pulldown(
        self,
        imports: Optional[dict[str, Any]] = None,
        module: Optional[Module] = None,
    ) -> _Pulldown:
        """
        Instantiate the "pulldown" library.
        :param imports: Additional imports to be provided to the WebAssembly
                        module.
        :param module: A user-specified WebAssembly module to use instead of the
                       one bundled with this package.
        """

        filename = "pulldown/pulldown-cmark.wasm"
        if not module:
            module = self._get_module(filename)

        if not imports:
            imports = {}

        return _Pulldown(self._store, imports, module)
    