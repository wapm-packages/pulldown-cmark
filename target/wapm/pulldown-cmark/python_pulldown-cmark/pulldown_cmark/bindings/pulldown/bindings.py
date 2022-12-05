from abc import abstractmethod
from dataclasses import dataclass
from enum import Flag, auto
from typing import Any, Callable, Generic, List, Optional, Tuple, TypeVar, Union
import wasmer # type: ignore

try:
    from typing import Protocol
except ImportError:
    class Protocol: # type: ignore
        pass

T = TypeVar('T')

def _load(make_view: Callable[[], Any], mem: wasmer.Memory, base: int, offset: int) -> Any:
    ptr = (base & 0xffffffff) + offset
    view = make_view()
    if ptr + view.bytes_per_element > mem.data_size:
        raise IndexError('out-of-bounds load')
    view_ptr = ptr // view.bytes_per_element
    return view[view_ptr]

@dataclass
class Ok(Generic[T]):
    value: T
E = TypeVar('E')
@dataclass
class Err(Generic[E]):
    value: E

Expected = Union[Ok[T], Err[E]]

def _decode_utf8(mem: wasmer.Memory, ptr: int, len: int) -> str:
    ptr = ptr & 0xffffffff
    len = len & 0xffffffff
    if ptr + len > mem.data_size:
        raise IndexError('string out of bounds')
    view = mem.uint8_view()
    bytes = bytearray(view[ptr:ptr+len])
    x = bytes.decode('utf8')
    return x

def _encode_utf8(val: str, realloc: wasmer.Function, mem: wasmer.Memory) -> Tuple[int, int]:
    bytes = val.encode('utf8')
    ptr = realloc(0, 0, 1, len(bytes))
    assert(isinstance(ptr, int))
    ptr = ptr & 0xffffffff
    if ptr + len(bytes) > mem.data_size:
        raise IndexError('string out of bounds')
    view = mem.uint8_view()
    view[ptr:ptr+len(bytes)] = bytes
    return (ptr, len(bytes))
@dataclass
class Error:
    message: str

CowStr = str
class Options(Flag):
    ENABLE_TABLES = auto()
    ENABLE_FOOTNOTES = auto()
    ENABLE_STRIKETHROUGH = auto()
    ENABLE_TASKLISTS = auto()
    ENABLE_SMART_PUNCTUATION = auto()
    ENABLE_HEADING_ATTRIBUTES = auto()

@dataclass
class AlignmentNone:
    value: None

@dataclass
class AlignmentLeft:
    value: None

@dataclass
class AlignmentCenter:
    value: None

@dataclass
class AlignmentRight:
    value: None

Alignment = Union[AlignmentNone, AlignmentLeft, AlignmentCenter, AlignmentRight]

@dataclass
class CodeBlockKindIndented:
    value: None

@dataclass
class CodeBlockKindFenced:
    value: 'CowStr'

CodeBlockKind = Union[CodeBlockKindIndented, CodeBlockKindFenced]

@dataclass
class LinkTypeInline:
    value: None

@dataclass
class LinkTypeReference:
    value: None

@dataclass
class LinkTypeReferenceUnknown:
    value: None

@dataclass
class LinkTypeCollapsed:
    value: None

@dataclass
class LinkTypeCollapsedUnknown:
    value: None

@dataclass
class LinkTypeShortcut:
    value: None

@dataclass
class LinkTypeShortcutUnknown:
    value: None

@dataclass
class LinkTypeAutolink:
    value: None

@dataclass
class LinkTypeEmail:
    value: None

LinkType = Union[LinkTypeInline, LinkTypeReference, LinkTypeReferenceUnknown, LinkTypeCollapsed, LinkTypeCollapsedUnknown, LinkTypeShortcut, LinkTypeShortcutUnknown, LinkTypeAutolink, LinkTypeEmail]

@dataclass
class HeadingLevelH1:
    value: None

@dataclass
class HeadingLevelH2:
    value: None

@dataclass
class HeadingLevelH3:
    value: None

@dataclass
class HeadingLevelH4:
    value: None

@dataclass
class HeadingLevelH5:
    value: None

@dataclass
class HeadingLevelH6:
    value: None

HeadingLevel = Union[HeadingLevelH1, HeadingLevelH2, HeadingLevelH3, HeadingLevelH4, HeadingLevelH5, HeadingLevelH6]

@dataclass
class TagParagraph:
    value: None

@dataclass
class TagHeading:
    value: Tuple['HeadingLevel', Optional[str], List[str]]

@dataclass
class TagBlockQuote:
    value: None

@dataclass
class TagCodeBlock:
    value: 'CodeBlockKind'

@dataclass
class TagListTag:
    value: Optional[int]

@dataclass
class TagItem:
    value: None

@dataclass
class TagFootnoteDefinition:
    value: 'CowStr'

@dataclass
class TagTable:
    value: List['Alignment']

@dataclass
class TagTableHead:
    value: None

@dataclass
class TagTableRow:
    value: None

@dataclass
class TagTableCell:
    value: None

@dataclass
class TagEmphasis:
    value: None

@dataclass
class TagStrong:
    value: None

@dataclass
class TagStrikeThrough:
    value: None

@dataclass
class TagLink:
    value: Tuple['LinkType', 'CowStr', 'CowStr']

@dataclass
class TagImage:
    value: Tuple['LinkType', 'CowStr', 'CowStr']

Tag = Union[TagParagraph, TagHeading, TagBlockQuote, TagCodeBlock, TagListTag, TagItem, TagFootnoteDefinition, TagTable, TagTableHead, TagTableRow, TagTableCell, TagEmphasis, TagStrong, TagStrikeThrough, TagLink, TagImage]

@dataclass
class EventStart:
    value: 'Tag'

@dataclass
class EventEnd:
    value: 'Tag'

@dataclass
class EventText:
    value: 'CowStr'

@dataclass
class EventCode:
    value: 'CowStr'

@dataclass
class EventHtml:
    value: 'CowStr'

@dataclass
class EventFootnoteReference:
    value: 'CowStr'

@dataclass
class EventSoftBreak:
    value: None

@dataclass
class EventHardBreak:
    value: None

@dataclass
class EventRule:
    value: None

@dataclass
class EventTaskListMarker:
    value: bool

Event = Union[EventStart, EventEnd, EventText, EventCode, EventHtml, EventFootnoteReference, EventSoftBreak, EventHardBreak, EventRule, EventTaskListMarker]

@dataclass
class Range:
    start: int
    end: int

@dataclass
class BrokenLink:
    span: 'Range'
    link_type: 'LinkType'
    reference: 'CowStr'

@dataclass
class InvalidHeadingLevel:
    message: str

@dataclass
class LinkDef:
    dest: 'CowStr'
    title: Optional['CowStr']
    span: 'Range'

OffsetItem = Tuple['Event', 'Range']
class Pulldown:
    instance: wasmer.Instance
    _canonical_abi_free: wasmer.Function
    _canonical_abi_realloc: wasmer.Function
    _escape_href: wasmer.Function
    _escape_html: wasmer.Function
    _markdown_to_html: wasmer.Function
    _memory: wasmer.Memory
    _parse: wasmer.Function
    _parse_with_options: wasmer.Function
    def __init__(self, store: wasmer.Store, imports: dict[str, dict[str, Any]], module: wasmer.Module):
        self.instance = wasmer.Instance(module, imports)
        
        canonical_abi_free = self.instance.exports.__getattribute__('canonical_abi_free')
        assert(isinstance(canonical_abi_free, wasmer.Function))
        self._canonical_abi_free = canonical_abi_free
        
        canonical_abi_realloc = self.instance.exports.__getattribute__('canonical_abi_realloc')
        assert(isinstance(canonical_abi_realloc, wasmer.Function))
        self._canonical_abi_realloc = canonical_abi_realloc
        
        escape_href = self.instance.exports.__getattribute__('escape-href')
        assert(isinstance(escape_href, wasmer.Function))
        self._escape_href = escape_href
        
        escape_html = self.instance.exports.__getattribute__('escape-html')
        assert(isinstance(escape_html, wasmer.Function))
        self._escape_html = escape_html
        
        markdown_to_html = self.instance.exports.__getattribute__('markdown-to-html')
        assert(isinstance(markdown_to_html, wasmer.Function))
        self._markdown_to_html = markdown_to_html
        
        memory = self.instance.exports.__getattribute__('memory')
        assert(isinstance(memory, wasmer.Memory))
        self._memory = memory
        
        parse = self.instance.exports.__getattribute__('parse')
        assert(isinstance(parse, wasmer.Function))
        self._parse = parse
        
        parse_with_options = self.instance.exports.__getattribute__('parse-with-options')
        assert(isinstance(parse_with_options, wasmer.Function))
        self._parse_with_options = parse_with_options
    def escape_href(self, s: str) -> Expected[str, 'Error']:
        memory = self._memory;
        realloc = self._canonical_abi_realloc
        free = self._canonical_abi_free
        ptr, len0 = _encode_utf8(s, realloc, memory)
        ret = self._escape_href(ptr, len0)
        assert(isinstance(ret, int))
        load = _load(memory.uint8_view, memory, ret, 0)
        expected: Expected[str, 'Error']
        if load == 0:
            load1 = _load(memory.int32_view, memory, ret, 4)
            load2 = _load(memory.int32_view, memory, ret, 8)
            ptr3 = load1
            len4 = load2
            list = _decode_utf8(memory, ptr3, len4)
            free(ptr3, len4, 1)
            expected = Ok(list)
        elif load == 1:
            load5 = _load(memory.int32_view, memory, ret, 4)
            load6 = _load(memory.int32_view, memory, ret, 8)
            ptr7 = load5
            len8 = load6
            list9 = _decode_utf8(memory, ptr7, len8)
            free(ptr7, len8, 1)
            expected = Err(Error(list9))
        else:
            raise TypeError("invalid variant discriminant for expected")
        return expected
    def escape_html(self, s: str) -> Expected[str, 'Error']:
        memory = self._memory;
        realloc = self._canonical_abi_realloc
        free = self._canonical_abi_free
        ptr, len0 = _encode_utf8(s, realloc, memory)
        ret = self._escape_html(ptr, len0)
        assert(isinstance(ret, int))
        load = _load(memory.uint8_view, memory, ret, 0)
        expected: Expected[str, 'Error']
        if load == 0:
            load1 = _load(memory.int32_view, memory, ret, 4)
            load2 = _load(memory.int32_view, memory, ret, 8)
            ptr3 = load1
            len4 = load2
            list = _decode_utf8(memory, ptr3, len4)
            free(ptr3, len4, 1)
            expected = Ok(list)
        elif load == 1:
            load5 = _load(memory.int32_view, memory, ret, 4)
            load6 = _load(memory.int32_view, memory, ret, 8)
            ptr7 = load5
            len8 = load6
            list9 = _decode_utf8(memory, ptr7, len8)
            free(ptr7, len8, 1)
            expected = Err(Error(list9))
        else:
            raise TypeError("invalid variant discriminant for expected")
        return expected
    def markdown_to_html(self, markdown_string: str) -> str:
        memory = self._memory;
        realloc = self._canonical_abi_realloc
        free = self._canonical_abi_free
        ptr, len0 = _encode_utf8(markdown_string, realloc, memory)
        ret = self._markdown_to_html(ptr, len0)
        assert(isinstance(ret, int))
        load = _load(memory.int32_view, memory, ret, 0)
        load1 = _load(memory.int32_view, memory, ret, 4)
        ptr2 = load
        len3 = load1
        list = _decode_utf8(memory, ptr2, len3)
        free(ptr2, len3, 1)
        return list
    def parse(self, markdown: str) -> List['OffsetItem']:
        memory = self._memory;
        realloc = self._canonical_abi_realloc
        free = self._canonical_abi_free
        ptr, len0 = _encode_utf8(markdown, realloc, memory)
        ret = self._parse(ptr, len0)
        assert(isinstance(ret, int))
        load = _load(memory.int32_view, memory, ret, 0)
        load1 = _load(memory.int32_view, memory, ret, 4)
        ptr166 = load
        len167 = load1
        result168: List['OffsetItem'] = []
        for i169 in range(0, len167):
            base2 = ptr166 + i169 * 48
            load3 = _load(memory.uint8_view, memory, base2, 0)
            variant163: 'Event'
            if load3 == 0:
                load4 = _load(memory.uint8_view, memory, base2, 8)
                variant70: 'Tag'
                if load4 == 0:
                    variant70 = TagParagraph(None)
                elif load4 == 1:
                    load5 = _load(memory.uint8_view, memory, base2, 16)
                    variant: 'HeadingLevel'
                    if load5 == 0:
                        variant = HeadingLevelH1(None)
                    elif load5 == 1:
                        variant = HeadingLevelH2(None)
                    elif load5 == 2:
                        variant = HeadingLevelH3(None)
                    elif load5 == 3:
                        variant = HeadingLevelH4(None)
                    elif load5 == 4:
                        variant = HeadingLevelH5(None)
                    elif load5 == 5:
                        variant = HeadingLevelH6(None)
                    else:
                        raise TypeError("invalid variant discriminant for HeadingLevel")
                    load6 = _load(memory.uint8_view, memory, base2, 20)
                    option: Optional[str]
                    if load6 == 0:
                        option = None
                    elif load6 == 1:
                        load7 = _load(memory.int32_view, memory, base2, 24)
                        load8 = _load(memory.int32_view, memory, base2, 28)
                        ptr9 = load7
                        len10 = load8
                        list = _decode_utf8(memory, ptr9, len10)
                        free(ptr9, len10, 1)
                        option = list
                    else:
                        raise TypeError("invalid variant discriminant for option")
                    load11 = _load(memory.int32_view, memory, base2, 32)
                    load12 = _load(memory.int32_view, memory, base2, 36)
                    ptr19 = load11
                    len20 = load12
                    result: List[str] = []
                    for i21 in range(0, len20):
                        base13 = ptr19 + i21 * 8
                        load14 = _load(memory.int32_view, memory, base13, 0)
                        load15 = _load(memory.int32_view, memory, base13, 4)
                        ptr16 = load14
                        len17 = load15
                        list18 = _decode_utf8(memory, ptr16, len17)
                        free(ptr16, len17, 1)
                        result.append(list18)
                    free(ptr19, len20 * 8, 4)
                    variant70 = TagHeading((variant, option, result,))
                elif load4 == 2:
                    variant70 = TagBlockQuote(None)
                elif load4 == 3:
                    load22 = _load(memory.uint8_view, memory, base2, 16)
                    variant28: 'CodeBlockKind'
                    if load22 == 0:
                        variant28 = CodeBlockKindIndented(None)
                    elif load22 == 1:
                        load23 = _load(memory.int32_view, memory, base2, 20)
                        load24 = _load(memory.int32_view, memory, base2, 24)
                        ptr25 = load23
                        len26 = load24
                        list27 = _decode_utf8(memory, ptr25, len26)
                        free(ptr25, len26, 1)
                        variant28 = CodeBlockKindFenced(list27)
                    else:
                        raise TypeError("invalid variant discriminant for CodeBlockKind")
                    variant70 = TagCodeBlock(variant28)
                elif load4 == 4:
                    load29 = _load(memory.uint8_view, memory, base2, 16)
                    option31: Optional[int]
                    if load29 == 0:
                        option31 = None
                    elif load29 == 1:
                        load30 = _load(memory.int64_view, memory, base2, 24)
                        option31 = load30 & 0xffffffffffffffff
                    else:
                        raise TypeError("invalid variant discriminant for option")
                    variant70 = TagListTag(option31)
                elif load4 == 5:
                    variant70 = TagItem(None)
                elif load4 == 6:
                    load32 = _load(memory.int32_view, memory, base2, 16)
                    load33 = _load(memory.int32_view, memory, base2, 20)
                    ptr34 = load32
                    len35 = load33
                    list36 = _decode_utf8(memory, ptr34, len35)
                    free(ptr34, len35, 1)
                    variant70 = TagFootnoteDefinition(list36)
                elif load4 == 7:
                    load37 = _load(memory.int32_view, memory, base2, 16)
                    load38 = _load(memory.int32_view, memory, base2, 20)
                    ptr42 = load37
                    len43 = load38
                    result44: List['Alignment'] = []
                    for i45 in range(0, len43):
                        base39 = ptr42 + i45 * 1
                        load40 = _load(memory.uint8_view, memory, base39, 0)
                        variant41: 'Alignment'
                        if load40 == 0:
                            variant41 = AlignmentNone(None)
                        elif load40 == 1:
                            variant41 = AlignmentLeft(None)
                        elif load40 == 2:
                            variant41 = AlignmentCenter(None)
                        elif load40 == 3:
                            variant41 = AlignmentRight(None)
                        else:
                            raise TypeError("invalid variant discriminant for Alignment")
                        result44.append(variant41)
                    free(ptr42, len43 * 1, 1)
                    variant70 = TagTable(result44)
                elif load4 == 8:
                    variant70 = TagTableHead(None)
                elif load4 == 9:
                    variant70 = TagTableRow(None)
                elif load4 == 10:
                    variant70 = TagTableCell(None)
                elif load4 == 11:
                    variant70 = TagEmphasis(None)
                elif load4 == 12:
                    variant70 = TagStrong(None)
                elif load4 == 13:
                    variant70 = TagStrikeThrough(None)
                elif load4 == 14:
                    load46 = _load(memory.uint8_view, memory, base2, 16)
                    variant47: 'LinkType'
                    if load46 == 0:
                        variant47 = LinkTypeInline(None)
                    elif load46 == 1:
                        variant47 = LinkTypeReference(None)
                    elif load46 == 2:
                        variant47 = LinkTypeReferenceUnknown(None)
                    elif load46 == 3:
                        variant47 = LinkTypeCollapsed(None)
                    elif load46 == 4:
                        variant47 = LinkTypeCollapsedUnknown(None)
                    elif load46 == 5:
                        variant47 = LinkTypeShortcut(None)
                    elif load46 == 6:
                        variant47 = LinkTypeShortcutUnknown(None)
                    elif load46 == 7:
                        variant47 = LinkTypeAutolink(None)
                    elif load46 == 8:
                        variant47 = LinkTypeEmail(None)
                    else:
                        raise TypeError("invalid variant discriminant for LinkType")
                    load48 = _load(memory.int32_view, memory, base2, 20)
                    load49 = _load(memory.int32_view, memory, base2, 24)
                    ptr50 = load48
                    len51 = load49
                    list52 = _decode_utf8(memory, ptr50, len51)
                    free(ptr50, len51, 1)
                    load53 = _load(memory.int32_view, memory, base2, 28)
                    load54 = _load(memory.int32_view, memory, base2, 32)
                    ptr55 = load53
                    len56 = load54
                    list57 = _decode_utf8(memory, ptr55, len56)
                    free(ptr55, len56, 1)
                    variant70 = TagLink((variant47, list52, list57,))
                elif load4 == 15:
                    load58 = _load(memory.uint8_view, memory, base2, 16)
                    variant59: 'LinkType'
                    if load58 == 0:
                        variant59 = LinkTypeInline(None)
                    elif load58 == 1:
                        variant59 = LinkTypeReference(None)
                    elif load58 == 2:
                        variant59 = LinkTypeReferenceUnknown(None)
                    elif load58 == 3:
                        variant59 = LinkTypeCollapsed(None)
                    elif load58 == 4:
                        variant59 = LinkTypeCollapsedUnknown(None)
                    elif load58 == 5:
                        variant59 = LinkTypeShortcut(None)
                    elif load58 == 6:
                        variant59 = LinkTypeShortcutUnknown(None)
                    elif load58 == 7:
                        variant59 = LinkTypeAutolink(None)
                    elif load58 == 8:
                        variant59 = LinkTypeEmail(None)
                    else:
                        raise TypeError("invalid variant discriminant for LinkType")
                    load60 = _load(memory.int32_view, memory, base2, 20)
                    load61 = _load(memory.int32_view, memory, base2, 24)
                    ptr62 = load60
                    len63 = load61
                    list64 = _decode_utf8(memory, ptr62, len63)
                    free(ptr62, len63, 1)
                    load65 = _load(memory.int32_view, memory, base2, 28)
                    load66 = _load(memory.int32_view, memory, base2, 32)
                    ptr67 = load65
                    len68 = load66
                    list69 = _decode_utf8(memory, ptr67, len68)
                    free(ptr67, len68, 1)
                    variant70 = TagImage((variant59, list64, list69,))
                else:
                    raise TypeError("invalid variant discriminant for Tag")
                variant163 = EventStart(variant70)
            elif load3 == 1:
                load71 = _load(memory.uint8_view, memory, base2, 8)
                variant141: 'Tag'
                if load71 == 0:
                    variant141 = TagParagraph(None)
                elif load71 == 1:
                    load72 = _load(memory.uint8_view, memory, base2, 16)
                    variant73: 'HeadingLevel'
                    if load72 == 0:
                        variant73 = HeadingLevelH1(None)
                    elif load72 == 1:
                        variant73 = HeadingLevelH2(None)
                    elif load72 == 2:
                        variant73 = HeadingLevelH3(None)
                    elif load72 == 3:
                        variant73 = HeadingLevelH4(None)
                    elif load72 == 4:
                        variant73 = HeadingLevelH5(None)
                    elif load72 == 5:
                        variant73 = HeadingLevelH6(None)
                    else:
                        raise TypeError("invalid variant discriminant for HeadingLevel")
                    load74 = _load(memory.uint8_view, memory, base2, 20)
                    option80: Optional[str]
                    if load74 == 0:
                        option80 = None
                    elif load74 == 1:
                        load75 = _load(memory.int32_view, memory, base2, 24)
                        load76 = _load(memory.int32_view, memory, base2, 28)
                        ptr77 = load75
                        len78 = load76
                        list79 = _decode_utf8(memory, ptr77, len78)
                        free(ptr77, len78, 1)
                        option80 = list79
                    else:
                        raise TypeError("invalid variant discriminant for option")
                    load81 = _load(memory.int32_view, memory, base2, 32)
                    load82 = _load(memory.int32_view, memory, base2, 36)
                    ptr89 = load81
                    len90 = load82
                    result91: List[str] = []
                    for i92 in range(0, len90):
                        base83 = ptr89 + i92 * 8
                        load84 = _load(memory.int32_view, memory, base83, 0)
                        load85 = _load(memory.int32_view, memory, base83, 4)
                        ptr86 = load84
                        len87 = load85
                        list88 = _decode_utf8(memory, ptr86, len87)
                        free(ptr86, len87, 1)
                        result91.append(list88)
                    free(ptr89, len90 * 8, 4)
                    variant141 = TagHeading((variant73, option80, result91,))
                elif load71 == 2:
                    variant141 = TagBlockQuote(None)
                elif load71 == 3:
                    load93 = _load(memory.uint8_view, memory, base2, 16)
                    variant99: 'CodeBlockKind'
                    if load93 == 0:
                        variant99 = CodeBlockKindIndented(None)
                    elif load93 == 1:
                        load94 = _load(memory.int32_view, memory, base2, 20)
                        load95 = _load(memory.int32_view, memory, base2, 24)
                        ptr96 = load94
                        len97 = load95
                        list98 = _decode_utf8(memory, ptr96, len97)
                        free(ptr96, len97, 1)
                        variant99 = CodeBlockKindFenced(list98)
                    else:
                        raise TypeError("invalid variant discriminant for CodeBlockKind")
                    variant141 = TagCodeBlock(variant99)
                elif load71 == 4:
                    load100 = _load(memory.uint8_view, memory, base2, 16)
                    option102: Optional[int]
                    if load100 == 0:
                        option102 = None
                    elif load100 == 1:
                        load101 = _load(memory.int64_view, memory, base2, 24)
                        option102 = load101 & 0xffffffffffffffff
                    else:
                        raise TypeError("invalid variant discriminant for option")
                    variant141 = TagListTag(option102)
                elif load71 == 5:
                    variant141 = TagItem(None)
                elif load71 == 6:
                    load103 = _load(memory.int32_view, memory, base2, 16)
                    load104 = _load(memory.int32_view, memory, base2, 20)
                    ptr105 = load103
                    len106 = load104
                    list107 = _decode_utf8(memory, ptr105, len106)
                    free(ptr105, len106, 1)
                    variant141 = TagFootnoteDefinition(list107)
                elif load71 == 7:
                    load108 = _load(memory.int32_view, memory, base2, 16)
                    load109 = _load(memory.int32_view, memory, base2, 20)
                    ptr113 = load108
                    len114 = load109
                    result115: List['Alignment'] = []
                    for i116 in range(0, len114):
                        base110 = ptr113 + i116 * 1
                        load111 = _load(memory.uint8_view, memory, base110, 0)
                        variant112: 'Alignment'
                        if load111 == 0:
                            variant112 = AlignmentNone(None)
                        elif load111 == 1:
                            variant112 = AlignmentLeft(None)
                        elif load111 == 2:
                            variant112 = AlignmentCenter(None)
                        elif load111 == 3:
                            variant112 = AlignmentRight(None)
                        else:
                            raise TypeError("invalid variant discriminant for Alignment")
                        result115.append(variant112)
                    free(ptr113, len114 * 1, 1)
                    variant141 = TagTable(result115)
                elif load71 == 8:
                    variant141 = TagTableHead(None)
                elif load71 == 9:
                    variant141 = TagTableRow(None)
                elif load71 == 10:
                    variant141 = TagTableCell(None)
                elif load71 == 11:
                    variant141 = TagEmphasis(None)
                elif load71 == 12:
                    variant141 = TagStrong(None)
                elif load71 == 13:
                    variant141 = TagStrikeThrough(None)
                elif load71 == 14:
                    load117 = _load(memory.uint8_view, memory, base2, 16)
                    variant118: 'LinkType'
                    if load117 == 0:
                        variant118 = LinkTypeInline(None)
                    elif load117 == 1:
                        variant118 = LinkTypeReference(None)
                    elif load117 == 2:
                        variant118 = LinkTypeReferenceUnknown(None)
                    elif load117 == 3:
                        variant118 = LinkTypeCollapsed(None)
                    elif load117 == 4:
                        variant118 = LinkTypeCollapsedUnknown(None)
                    elif load117 == 5:
                        variant118 = LinkTypeShortcut(None)
                    elif load117 == 6:
                        variant118 = LinkTypeShortcutUnknown(None)
                    elif load117 == 7:
                        variant118 = LinkTypeAutolink(None)
                    elif load117 == 8:
                        variant118 = LinkTypeEmail(None)
                    else:
                        raise TypeError("invalid variant discriminant for LinkType")
                    load119 = _load(memory.int32_view, memory, base2, 20)
                    load120 = _load(memory.int32_view, memory, base2, 24)
                    ptr121 = load119
                    len122 = load120
                    list123 = _decode_utf8(memory, ptr121, len122)
                    free(ptr121, len122, 1)
                    load124 = _load(memory.int32_view, memory, base2, 28)
                    load125 = _load(memory.int32_view, memory, base2, 32)
                    ptr126 = load124
                    len127 = load125
                    list128 = _decode_utf8(memory, ptr126, len127)
                    free(ptr126, len127, 1)
                    variant141 = TagLink((variant118, list123, list128,))
                elif load71 == 15:
                    load129 = _load(memory.uint8_view, memory, base2, 16)
                    variant130: 'LinkType'
                    if load129 == 0:
                        variant130 = LinkTypeInline(None)
                    elif load129 == 1:
                        variant130 = LinkTypeReference(None)
                    elif load129 == 2:
                        variant130 = LinkTypeReferenceUnknown(None)
                    elif load129 == 3:
                        variant130 = LinkTypeCollapsed(None)
                    elif load129 == 4:
                        variant130 = LinkTypeCollapsedUnknown(None)
                    elif load129 == 5:
                        variant130 = LinkTypeShortcut(None)
                    elif load129 == 6:
                        variant130 = LinkTypeShortcutUnknown(None)
                    elif load129 == 7:
                        variant130 = LinkTypeAutolink(None)
                    elif load129 == 8:
                        variant130 = LinkTypeEmail(None)
                    else:
                        raise TypeError("invalid variant discriminant for LinkType")
                    load131 = _load(memory.int32_view, memory, base2, 20)
                    load132 = _load(memory.int32_view, memory, base2, 24)
                    ptr133 = load131
                    len134 = load132
                    list135 = _decode_utf8(memory, ptr133, len134)
                    free(ptr133, len134, 1)
                    load136 = _load(memory.int32_view, memory, base2, 28)
                    load137 = _load(memory.int32_view, memory, base2, 32)
                    ptr138 = load136
                    len139 = load137
                    list140 = _decode_utf8(memory, ptr138, len139)
                    free(ptr138, len139, 1)
                    variant141 = TagImage((variant130, list135, list140,))
                else:
                    raise TypeError("invalid variant discriminant for Tag")
                variant163 = EventEnd(variant141)
            elif load3 == 2:
                load142 = _load(memory.int32_view, memory, base2, 8)
                load143 = _load(memory.int32_view, memory, base2, 12)
                ptr144 = load142
                len145 = load143
                list146 = _decode_utf8(memory, ptr144, len145)
                free(ptr144, len145, 1)
                variant163 = EventText(list146)
            elif load3 == 3:
                load147 = _load(memory.int32_view, memory, base2, 8)
                load148 = _load(memory.int32_view, memory, base2, 12)
                ptr149 = load147
                len150 = load148
                list151 = _decode_utf8(memory, ptr149, len150)
                free(ptr149, len150, 1)
                variant163 = EventCode(list151)
            elif load3 == 4:
                load152 = _load(memory.int32_view, memory, base2, 8)
                load153 = _load(memory.int32_view, memory, base2, 12)
                ptr154 = load152
                len155 = load153
                list156 = _decode_utf8(memory, ptr154, len155)
                free(ptr154, len155, 1)
                variant163 = EventHtml(list156)
            elif load3 == 5:
                load157 = _load(memory.int32_view, memory, base2, 8)
                load158 = _load(memory.int32_view, memory, base2, 12)
                ptr159 = load157
                len160 = load158
                list161 = _decode_utf8(memory, ptr159, len160)
                free(ptr159, len160, 1)
                variant163 = EventFootnoteReference(list161)
            elif load3 == 6:
                variant163 = EventSoftBreak(None)
            elif load3 == 7:
                variant163 = EventHardBreak(None)
            elif load3 == 8:
                variant163 = EventRule(None)
            elif load3 == 9:
                load162 = _load(memory.uint8_view, memory, base2, 8)
                
                operand = load162
                if operand == 0:
                    boolean = False
                elif operand == 1:
                    boolean = True
                else:
                    raise TypeError("invalid variant discriminant for bool")
                variant163 = EventTaskListMarker(boolean)
            else:
                raise TypeError("invalid variant discriminant for Event")
            load164 = _load(memory.int32_view, memory, base2, 36)
            load165 = _load(memory.int32_view, memory, base2, 40)
            result168.append((variant163, Range(load164 & 0xffffffff, load165 & 0xffffffff),))
        free(ptr166, len167 * 48, 8)
        return result168
    def parse_with_options(self, markdown: str, options: 'Options') -> List['OffsetItem']:
        memory = self._memory;
        realloc = self._canonical_abi_realloc
        free = self._canonical_abi_free
        ptr, len0 = _encode_utf8(markdown, realloc, memory)
        ret = self._parse_with_options(ptr, len0, (options).value)
        assert(isinstance(ret, int))
        load = _load(memory.int32_view, memory, ret, 0)
        load1 = _load(memory.int32_view, memory, ret, 4)
        ptr166 = load
        len167 = load1
        result168: List['OffsetItem'] = []
        for i169 in range(0, len167):
            base2 = ptr166 + i169 * 48
            load3 = _load(memory.uint8_view, memory, base2, 0)
            variant163: 'Event'
            if load3 == 0:
                load4 = _load(memory.uint8_view, memory, base2, 8)
                variant70: 'Tag'
                if load4 == 0:
                    variant70 = TagParagraph(None)
                elif load4 == 1:
                    load5 = _load(memory.uint8_view, memory, base2, 16)
                    variant: 'HeadingLevel'
                    if load5 == 0:
                        variant = HeadingLevelH1(None)
                    elif load5 == 1:
                        variant = HeadingLevelH2(None)
                    elif load5 == 2:
                        variant = HeadingLevelH3(None)
                    elif load5 == 3:
                        variant = HeadingLevelH4(None)
                    elif load5 == 4:
                        variant = HeadingLevelH5(None)
                    elif load5 == 5:
                        variant = HeadingLevelH6(None)
                    else:
                        raise TypeError("invalid variant discriminant for HeadingLevel")
                    load6 = _load(memory.uint8_view, memory, base2, 20)
                    option: Optional[str]
                    if load6 == 0:
                        option = None
                    elif load6 == 1:
                        load7 = _load(memory.int32_view, memory, base2, 24)
                        load8 = _load(memory.int32_view, memory, base2, 28)
                        ptr9 = load7
                        len10 = load8
                        list = _decode_utf8(memory, ptr9, len10)
                        free(ptr9, len10, 1)
                        option = list
                    else:
                        raise TypeError("invalid variant discriminant for option")
                    load11 = _load(memory.int32_view, memory, base2, 32)
                    load12 = _load(memory.int32_view, memory, base2, 36)
                    ptr19 = load11
                    len20 = load12
                    result: List[str] = []
                    for i21 in range(0, len20):
                        base13 = ptr19 + i21 * 8
                        load14 = _load(memory.int32_view, memory, base13, 0)
                        load15 = _load(memory.int32_view, memory, base13, 4)
                        ptr16 = load14
                        len17 = load15
                        list18 = _decode_utf8(memory, ptr16, len17)
                        free(ptr16, len17, 1)
                        result.append(list18)
                    free(ptr19, len20 * 8, 4)
                    variant70 = TagHeading((variant, option, result,))
                elif load4 == 2:
                    variant70 = TagBlockQuote(None)
                elif load4 == 3:
                    load22 = _load(memory.uint8_view, memory, base2, 16)
                    variant28: 'CodeBlockKind'
                    if load22 == 0:
                        variant28 = CodeBlockKindIndented(None)
                    elif load22 == 1:
                        load23 = _load(memory.int32_view, memory, base2, 20)
                        load24 = _load(memory.int32_view, memory, base2, 24)
                        ptr25 = load23
                        len26 = load24
                        list27 = _decode_utf8(memory, ptr25, len26)
                        free(ptr25, len26, 1)
                        variant28 = CodeBlockKindFenced(list27)
                    else:
                        raise TypeError("invalid variant discriminant for CodeBlockKind")
                    variant70 = TagCodeBlock(variant28)
                elif load4 == 4:
                    load29 = _load(memory.uint8_view, memory, base2, 16)
                    option31: Optional[int]
                    if load29 == 0:
                        option31 = None
                    elif load29 == 1:
                        load30 = _load(memory.int64_view, memory, base2, 24)
                        option31 = load30 & 0xffffffffffffffff
                    else:
                        raise TypeError("invalid variant discriminant for option")
                    variant70 = TagListTag(option31)
                elif load4 == 5:
                    variant70 = TagItem(None)
                elif load4 == 6:
                    load32 = _load(memory.int32_view, memory, base2, 16)
                    load33 = _load(memory.int32_view, memory, base2, 20)
                    ptr34 = load32
                    len35 = load33
                    list36 = _decode_utf8(memory, ptr34, len35)
                    free(ptr34, len35, 1)
                    variant70 = TagFootnoteDefinition(list36)
                elif load4 == 7:
                    load37 = _load(memory.int32_view, memory, base2, 16)
                    load38 = _load(memory.int32_view, memory, base2, 20)
                    ptr42 = load37
                    len43 = load38
                    result44: List['Alignment'] = []
                    for i45 in range(0, len43):
                        base39 = ptr42 + i45 * 1
                        load40 = _load(memory.uint8_view, memory, base39, 0)
                        variant41: 'Alignment'
                        if load40 == 0:
                            variant41 = AlignmentNone(None)
                        elif load40 == 1:
                            variant41 = AlignmentLeft(None)
                        elif load40 == 2:
                            variant41 = AlignmentCenter(None)
                        elif load40 == 3:
                            variant41 = AlignmentRight(None)
                        else:
                            raise TypeError("invalid variant discriminant for Alignment")
                        result44.append(variant41)
                    free(ptr42, len43 * 1, 1)
                    variant70 = TagTable(result44)
                elif load4 == 8:
                    variant70 = TagTableHead(None)
                elif load4 == 9:
                    variant70 = TagTableRow(None)
                elif load4 == 10:
                    variant70 = TagTableCell(None)
                elif load4 == 11:
                    variant70 = TagEmphasis(None)
                elif load4 == 12:
                    variant70 = TagStrong(None)
                elif load4 == 13:
                    variant70 = TagStrikeThrough(None)
                elif load4 == 14:
                    load46 = _load(memory.uint8_view, memory, base2, 16)
                    variant47: 'LinkType'
                    if load46 == 0:
                        variant47 = LinkTypeInline(None)
                    elif load46 == 1:
                        variant47 = LinkTypeReference(None)
                    elif load46 == 2:
                        variant47 = LinkTypeReferenceUnknown(None)
                    elif load46 == 3:
                        variant47 = LinkTypeCollapsed(None)
                    elif load46 == 4:
                        variant47 = LinkTypeCollapsedUnknown(None)
                    elif load46 == 5:
                        variant47 = LinkTypeShortcut(None)
                    elif load46 == 6:
                        variant47 = LinkTypeShortcutUnknown(None)
                    elif load46 == 7:
                        variant47 = LinkTypeAutolink(None)
                    elif load46 == 8:
                        variant47 = LinkTypeEmail(None)
                    else:
                        raise TypeError("invalid variant discriminant for LinkType")
                    load48 = _load(memory.int32_view, memory, base2, 20)
                    load49 = _load(memory.int32_view, memory, base2, 24)
                    ptr50 = load48
                    len51 = load49
                    list52 = _decode_utf8(memory, ptr50, len51)
                    free(ptr50, len51, 1)
                    load53 = _load(memory.int32_view, memory, base2, 28)
                    load54 = _load(memory.int32_view, memory, base2, 32)
                    ptr55 = load53
                    len56 = load54
                    list57 = _decode_utf8(memory, ptr55, len56)
                    free(ptr55, len56, 1)
                    variant70 = TagLink((variant47, list52, list57,))
                elif load4 == 15:
                    load58 = _load(memory.uint8_view, memory, base2, 16)
                    variant59: 'LinkType'
                    if load58 == 0:
                        variant59 = LinkTypeInline(None)
                    elif load58 == 1:
                        variant59 = LinkTypeReference(None)
                    elif load58 == 2:
                        variant59 = LinkTypeReferenceUnknown(None)
                    elif load58 == 3:
                        variant59 = LinkTypeCollapsed(None)
                    elif load58 == 4:
                        variant59 = LinkTypeCollapsedUnknown(None)
                    elif load58 == 5:
                        variant59 = LinkTypeShortcut(None)
                    elif load58 == 6:
                        variant59 = LinkTypeShortcutUnknown(None)
                    elif load58 == 7:
                        variant59 = LinkTypeAutolink(None)
                    elif load58 == 8:
                        variant59 = LinkTypeEmail(None)
                    else:
                        raise TypeError("invalid variant discriminant for LinkType")
                    load60 = _load(memory.int32_view, memory, base2, 20)
                    load61 = _load(memory.int32_view, memory, base2, 24)
                    ptr62 = load60
                    len63 = load61
                    list64 = _decode_utf8(memory, ptr62, len63)
                    free(ptr62, len63, 1)
                    load65 = _load(memory.int32_view, memory, base2, 28)
                    load66 = _load(memory.int32_view, memory, base2, 32)
                    ptr67 = load65
                    len68 = load66
                    list69 = _decode_utf8(memory, ptr67, len68)
                    free(ptr67, len68, 1)
                    variant70 = TagImage((variant59, list64, list69,))
                else:
                    raise TypeError("invalid variant discriminant for Tag")
                variant163 = EventStart(variant70)
            elif load3 == 1:
                load71 = _load(memory.uint8_view, memory, base2, 8)
                variant141: 'Tag'
                if load71 == 0:
                    variant141 = TagParagraph(None)
                elif load71 == 1:
                    load72 = _load(memory.uint8_view, memory, base2, 16)
                    variant73: 'HeadingLevel'
                    if load72 == 0:
                        variant73 = HeadingLevelH1(None)
                    elif load72 == 1:
                        variant73 = HeadingLevelH2(None)
                    elif load72 == 2:
                        variant73 = HeadingLevelH3(None)
                    elif load72 == 3:
                        variant73 = HeadingLevelH4(None)
                    elif load72 == 4:
                        variant73 = HeadingLevelH5(None)
                    elif load72 == 5:
                        variant73 = HeadingLevelH6(None)
                    else:
                        raise TypeError("invalid variant discriminant for HeadingLevel")
                    load74 = _load(memory.uint8_view, memory, base2, 20)
                    option80: Optional[str]
                    if load74 == 0:
                        option80 = None
                    elif load74 == 1:
                        load75 = _load(memory.int32_view, memory, base2, 24)
                        load76 = _load(memory.int32_view, memory, base2, 28)
                        ptr77 = load75
                        len78 = load76
                        list79 = _decode_utf8(memory, ptr77, len78)
                        free(ptr77, len78, 1)
                        option80 = list79
                    else:
                        raise TypeError("invalid variant discriminant for option")
                    load81 = _load(memory.int32_view, memory, base2, 32)
                    load82 = _load(memory.int32_view, memory, base2, 36)
                    ptr89 = load81
                    len90 = load82
                    result91: List[str] = []
                    for i92 in range(0, len90):
                        base83 = ptr89 + i92 * 8
                        load84 = _load(memory.int32_view, memory, base83, 0)
                        load85 = _load(memory.int32_view, memory, base83, 4)
                        ptr86 = load84
                        len87 = load85
                        list88 = _decode_utf8(memory, ptr86, len87)
                        free(ptr86, len87, 1)
                        result91.append(list88)
                    free(ptr89, len90 * 8, 4)
                    variant141 = TagHeading((variant73, option80, result91,))
                elif load71 == 2:
                    variant141 = TagBlockQuote(None)
                elif load71 == 3:
                    load93 = _load(memory.uint8_view, memory, base2, 16)
                    variant99: 'CodeBlockKind'
                    if load93 == 0:
                        variant99 = CodeBlockKindIndented(None)
                    elif load93 == 1:
                        load94 = _load(memory.int32_view, memory, base2, 20)
                        load95 = _load(memory.int32_view, memory, base2, 24)
                        ptr96 = load94
                        len97 = load95
                        list98 = _decode_utf8(memory, ptr96, len97)
                        free(ptr96, len97, 1)
                        variant99 = CodeBlockKindFenced(list98)
                    else:
                        raise TypeError("invalid variant discriminant for CodeBlockKind")
                    variant141 = TagCodeBlock(variant99)
                elif load71 == 4:
                    load100 = _load(memory.uint8_view, memory, base2, 16)
                    option102: Optional[int]
                    if load100 == 0:
                        option102 = None
                    elif load100 == 1:
                        load101 = _load(memory.int64_view, memory, base2, 24)
                        option102 = load101 & 0xffffffffffffffff
                    else:
                        raise TypeError("invalid variant discriminant for option")
                    variant141 = TagListTag(option102)
                elif load71 == 5:
                    variant141 = TagItem(None)
                elif load71 == 6:
                    load103 = _load(memory.int32_view, memory, base2, 16)
                    load104 = _load(memory.int32_view, memory, base2, 20)
                    ptr105 = load103
                    len106 = load104
                    list107 = _decode_utf8(memory, ptr105, len106)
                    free(ptr105, len106, 1)
                    variant141 = TagFootnoteDefinition(list107)
                elif load71 == 7:
                    load108 = _load(memory.int32_view, memory, base2, 16)
                    load109 = _load(memory.int32_view, memory, base2, 20)
                    ptr113 = load108
                    len114 = load109
                    result115: List['Alignment'] = []
                    for i116 in range(0, len114):
                        base110 = ptr113 + i116 * 1
                        load111 = _load(memory.uint8_view, memory, base110, 0)
                        variant112: 'Alignment'
                        if load111 == 0:
                            variant112 = AlignmentNone(None)
                        elif load111 == 1:
                            variant112 = AlignmentLeft(None)
                        elif load111 == 2:
                            variant112 = AlignmentCenter(None)
                        elif load111 == 3:
                            variant112 = AlignmentRight(None)
                        else:
                            raise TypeError("invalid variant discriminant for Alignment")
                        result115.append(variant112)
                    free(ptr113, len114 * 1, 1)
                    variant141 = TagTable(result115)
                elif load71 == 8:
                    variant141 = TagTableHead(None)
                elif load71 == 9:
                    variant141 = TagTableRow(None)
                elif load71 == 10:
                    variant141 = TagTableCell(None)
                elif load71 == 11:
                    variant141 = TagEmphasis(None)
                elif load71 == 12:
                    variant141 = TagStrong(None)
                elif load71 == 13:
                    variant141 = TagStrikeThrough(None)
                elif load71 == 14:
                    load117 = _load(memory.uint8_view, memory, base2, 16)
                    variant118: 'LinkType'
                    if load117 == 0:
                        variant118 = LinkTypeInline(None)
                    elif load117 == 1:
                        variant118 = LinkTypeReference(None)
                    elif load117 == 2:
                        variant118 = LinkTypeReferenceUnknown(None)
                    elif load117 == 3:
                        variant118 = LinkTypeCollapsed(None)
                    elif load117 == 4:
                        variant118 = LinkTypeCollapsedUnknown(None)
                    elif load117 == 5:
                        variant118 = LinkTypeShortcut(None)
                    elif load117 == 6:
                        variant118 = LinkTypeShortcutUnknown(None)
                    elif load117 == 7:
                        variant118 = LinkTypeAutolink(None)
                    elif load117 == 8:
                        variant118 = LinkTypeEmail(None)
                    else:
                        raise TypeError("invalid variant discriminant for LinkType")
                    load119 = _load(memory.int32_view, memory, base2, 20)
                    load120 = _load(memory.int32_view, memory, base2, 24)
                    ptr121 = load119
                    len122 = load120
                    list123 = _decode_utf8(memory, ptr121, len122)
                    free(ptr121, len122, 1)
                    load124 = _load(memory.int32_view, memory, base2, 28)
                    load125 = _load(memory.int32_view, memory, base2, 32)
                    ptr126 = load124
                    len127 = load125
                    list128 = _decode_utf8(memory, ptr126, len127)
                    free(ptr126, len127, 1)
                    variant141 = TagLink((variant118, list123, list128,))
                elif load71 == 15:
                    load129 = _load(memory.uint8_view, memory, base2, 16)
                    variant130: 'LinkType'
                    if load129 == 0:
                        variant130 = LinkTypeInline(None)
                    elif load129 == 1:
                        variant130 = LinkTypeReference(None)
                    elif load129 == 2:
                        variant130 = LinkTypeReferenceUnknown(None)
                    elif load129 == 3:
                        variant130 = LinkTypeCollapsed(None)
                    elif load129 == 4:
                        variant130 = LinkTypeCollapsedUnknown(None)
                    elif load129 == 5:
                        variant130 = LinkTypeShortcut(None)
                    elif load129 == 6:
                        variant130 = LinkTypeShortcutUnknown(None)
                    elif load129 == 7:
                        variant130 = LinkTypeAutolink(None)
                    elif load129 == 8:
                        variant130 = LinkTypeEmail(None)
                    else:
                        raise TypeError("invalid variant discriminant for LinkType")
                    load131 = _load(memory.int32_view, memory, base2, 20)
                    load132 = _load(memory.int32_view, memory, base2, 24)
                    ptr133 = load131
                    len134 = load132
                    list135 = _decode_utf8(memory, ptr133, len134)
                    free(ptr133, len134, 1)
                    load136 = _load(memory.int32_view, memory, base2, 28)
                    load137 = _load(memory.int32_view, memory, base2, 32)
                    ptr138 = load136
                    len139 = load137
                    list140 = _decode_utf8(memory, ptr138, len139)
                    free(ptr138, len139, 1)
                    variant141 = TagImage((variant130, list135, list140,))
                else:
                    raise TypeError("invalid variant discriminant for Tag")
                variant163 = EventEnd(variant141)
            elif load3 == 2:
                load142 = _load(memory.int32_view, memory, base2, 8)
                load143 = _load(memory.int32_view, memory, base2, 12)
                ptr144 = load142
                len145 = load143
                list146 = _decode_utf8(memory, ptr144, len145)
                free(ptr144, len145, 1)
                variant163 = EventText(list146)
            elif load3 == 3:
                load147 = _load(memory.int32_view, memory, base2, 8)
                load148 = _load(memory.int32_view, memory, base2, 12)
                ptr149 = load147
                len150 = load148
                list151 = _decode_utf8(memory, ptr149, len150)
                free(ptr149, len150, 1)
                variant163 = EventCode(list151)
            elif load3 == 4:
                load152 = _load(memory.int32_view, memory, base2, 8)
                load153 = _load(memory.int32_view, memory, base2, 12)
                ptr154 = load152
                len155 = load153
                list156 = _decode_utf8(memory, ptr154, len155)
                free(ptr154, len155, 1)
                variant163 = EventHtml(list156)
            elif load3 == 5:
                load157 = _load(memory.int32_view, memory, base2, 8)
                load158 = _load(memory.int32_view, memory, base2, 12)
                ptr159 = load157
                len160 = load158
                list161 = _decode_utf8(memory, ptr159, len160)
                free(ptr159, len160, 1)
                variant163 = EventFootnoteReference(list161)
            elif load3 == 6:
                variant163 = EventSoftBreak(None)
            elif load3 == 7:
                variant163 = EventHardBreak(None)
            elif load3 == 8:
                variant163 = EventRule(None)
            elif load3 == 9:
                load162 = _load(memory.uint8_view, memory, base2, 8)
                
                operand = load162
                if operand == 0:
                    boolean = False
                elif operand == 1:
                    boolean = True
                else:
                    raise TypeError("invalid variant discriminant for bool")
                variant163 = EventTaskListMarker(boolean)
            else:
                raise TypeError("invalid variant discriminant for Event")
            load164 = _load(memory.int32_view, memory, base2, 36)
            load165 = _load(memory.int32_view, memory, base2, 40)
            result168.append((variant163, Range(load164 & 0xffffffff, load165 & 0xffffffff),))
        free(ptr166, len167 * 48, 8)
        return result168
