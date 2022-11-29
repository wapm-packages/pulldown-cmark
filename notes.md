pub struct Options { /_ private fields _/ }

const Enable options can be flags or enums of u8 ?

> use bag of bools [flags]
> all other methods are helpers in options class so don't make it
> keep it just flags and no requirement of methods on it, just implement from trait for conversion

Ask what is Event<'a>?

Read about lifetimes probably

> _'a_ ['identifier ] is a lifetime annotation, it's says whatever it's attached to
> 'a in pulldown\*cmark is the lifetime of the string that we are passing
> _'static_
> Event would be enum but should CowStr be implemented?
>
> lifetimes are everywhere so that we avoid copying code and dangling references so we use lifetimes and it's like a name to a scope
> if &str is an arguement to a function, it's a lifetime already but we just don't assign a name for the lifetime
> but in this case parser lives on for a while so we need a name for the lifetime
> event's lifetime is tied to the parser's lifetime so we need a common name for that for reuse across both

> lifetimes are just a rust concept and doesn't exist in webassembly
>
> two solutions:

- copy all the strings instead of using borrowed strings and early select the parser iterator into a Vec<Event>
- callback based approach - the host gives webassembly a callback that gets executed on each event

'\_ is a lifetime without a name

here when we pass &markdown
when we call `callback(event)`, the host will be given a direct references into webassembly linear memory with no copying.

```rust
fn parse(markdown: String,callback: fn (event: Event<'_>)){
    let parser = Parser::new(&markdown);
    for event in parser {
        callback(event);
    }
}
```

// same implemented
pub enum LinkType {
Inline,
Reference,
ReferenceUnknown,
Collapsed,
CollapsedUnknown,
Shortcut,
ShortcutUnknown,
Autolink,
Email,
}

pub enum HeadingLevel {
H1,
H2,
H3,
H4,
H5,
H6,
}

pub enum Tag<'a> {
Paragraph,
Heading(HeadingLevel, Option<&'a str>, Vec<&'a str>),
BlockQuote,
CodeBlock(CodeBlockKind<'a>),
List(Option<u64>),
Item,
FootnoteDefinition(CowStr<'a>),
Table(Vec<Alignment>),
TableHead,
TableRow,
TableCell,
Emphasis,
Strong,
Strikethrough,
Link(LinkType, CowStr<'a>, CowStr<'a>),
Image(LinkType, CowStr<'a>, CowStr<'a>),
}

pub enum Alignment {
None,
Left,
Center,
Right,
}

> would be implemented using `string`, all three would be string.
> this is the core difference between the guest and host code. because of this we are able to generate without using copies.
> In strategy 1, we would need to call `.into_string` to copy the string and return it.

```rust
pub enum CowStr<'a> {
    Boxed(Box<str>),
    Borrowed(&'a str),
    Inlined(InlineStr),
}
```

Modules:

make this into a resource--
pulldown_cmark::escape

pub trait StrWrite {
fn write*str(&mut self, s: &str) -> Result<()>;
fn write_fmt(&mut self, args: Arguments<'*>) -> Result<()>;
}

//make parser into a top level function as if we implement in a resource we have to implement a self referencing type

```rust

struct SelfRef{
    buffer: String,
    current_line: &str,
}

let buffer="Hello world".to_string();

let a=SelfRef {
    buffer,
    current_line: &buffer
}

```

//top level functions for both escape and html module

escape_href: Writes an href to the buffer, escaping href unsafe bytes.
escape_html: Writes the given string to the Write sink, replacing special HTML bytes (<, >, &, “) by escape sequences.

pulldown_cmark::html

push_html: Iterate over an Iterator of Events, generate HTML for each Event, and push it to a String.
write_html: Iterate over an Iterator of Events, generate HTML for each Event, and write it out to a writable stream.

// but how implement an iterator?
pub fn write_html<'a, I, W>(writer: W, iter: I) -> Result<()>
where
I: Iterator<Item = Event<'a>>,
W: Write,

// resource again
pub struct Parser<'input, 'callback> { /_ private fields _/ }
