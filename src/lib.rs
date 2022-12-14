use crate::pulldown::{
    Alignment, CodeBlockKind, Error, Event, HeadingLevel, LinkType, OffsetItem, Options, Range, Tag,
};

use original::{self};

wai_bindgen_rust::export!("pulldown.wai");

struct Pulldown;

impl pulldown::Pulldown for Pulldown {
    fn escape_href(s: String) -> Result<String, Error> {
        let mut temp = String::new();
        match original::escape::escape_href(&mut temp, &s) {
            Ok(_) => Ok(temp),
            Err(e) => Err(e.into()),
        }
    }

    fn escape_html(s: String) -> Result<String, Error> {
        let mut temp = String::new();
        match original::escape::escape_html(&mut temp, &s) {
            Ok(_) => Ok(temp),
            Err(e) => Err(e.into()),
        }
    }

    fn markdown_to_html(markdown_string: String) -> String {
        let parser = original::Parser::new(&markdown_string);
        let mut html_buf = String::new();
        original::html::push_html(&mut html_buf, parser);
        html_buf
    }

    fn parse(markdown: String) -> Vec<OffsetItem> {
        original::Parser::new(&markdown)
            .into_offset_iter()
            .map(|(e, r)| (e.into(), r.into()))
            .collect()
    }

    fn parse_with_options(markdown: String, options: Options) -> Vec<OffsetItem> {
        original::Parser::new_ext(&markdown, options.into())
            .into_offset_iter()
            .map(|(e, r)| (e.into(), r.into()))
            .collect()
    }
}

impl From<std::ops::Range<usize>> for Range {
    fn from(r: std::ops::Range<usize>) -> Self {
        pulldown::Range {
            start: r.start.try_into().unwrap(),
            end: r.end.try_into().unwrap(),
        }
    }
}

impl From<std::io::Error> for Error {
    fn from(e: std::io::Error) -> Self {
        Error {
            message: e.to_string(),
        }
    }
}

impl From<original::LinkType> for LinkType {
    fn from(link_type: original::LinkType) -> Self {
        match link_type {
            original::LinkType::Inline => LinkType::Inline,
            original::LinkType::Reference => LinkType::Reference,
            original::LinkType::ReferenceUnknown => LinkType::ReferenceUnknown,
            original::LinkType::Collapsed => LinkType::Collapsed,
            original::LinkType::CollapsedUnknown => LinkType::CollapsedUnknown,
            original::LinkType::Shortcut => LinkType::Shortcut,
            original::LinkType::ShortcutUnknown => LinkType::ShortcutUnknown,
            original::LinkType::Autolink => LinkType::Autolink,
            original::LinkType::Email => LinkType::Email,
        }
    }
}
impl<'a> From<original::CodeBlockKind<'a>> for CodeBlockKind {
    fn from(cbk: original::CodeBlockKind<'a>) -> Self {
        match cbk {
            original::CodeBlockKind::Indented => CodeBlockKind::Indented,
            original::CodeBlockKind::Fenced(s) => CodeBlockKind::Fenced(s.into_string()),
        }
    }
}

impl From<original::Alignment> for Alignment {
    fn from(alignment: original::Alignment) -> Self {
        match alignment {
            original::Alignment::None => Alignment::None,
            original::Alignment::Left => Alignment::Left,
            original::Alignment::Center => Alignment::Center,
            original::Alignment::Right => Alignment::Right,
        }
    }
}

impl From<original::HeadingLevel> for HeadingLevel {
    fn from(heading_level: original::HeadingLevel) -> Self {
        match heading_level {
            original::HeadingLevel::H1 => HeadingLevel::H1,
            original::HeadingLevel::H2 => HeadingLevel::H2,
            original::HeadingLevel::H3 => HeadingLevel::H3,
            original::HeadingLevel::H4 => HeadingLevel::H4,
            original::HeadingLevel::H5 => HeadingLevel::H5,
            original::HeadingLevel::H6 => HeadingLevel::H6,
        }
    }
}

impl From<original::Tag<'_>> for Tag {
    fn from(tag: original::Tag<'_>) -> Self {
        match tag {
            original::Tag::Paragraph => Tag::Paragraph,
            original::Tag::Heading(heading_level, s, str_arr) => Tag::Heading((
                heading_level.into(),
                s.map(ToString::to_string),
                str_arr.iter().map(|&s| s.into()).collect(),
            )),
            original::Tag::BlockQuote => Tag::BlockQuote,
            original::Tag::CodeBlock(cbk) => Tag::CodeBlock(cbk.into()),
            original::Tag::List(l) => Tag::ListTag(l),
            original::Tag::Item => Tag::Item,
            original::Tag::FootnoteDefinition(s) => Tag::FootnoteDefinition(s.into_string()),
            original::Tag::Table(alignments) => {
                Tag::Table(alignments.iter().map(|&a| a.into()).collect())
            }
            original::Tag::TableHead => Tag::TableHead,
            original::Tag::TableRow => Tag::TableRow,
            original::Tag::TableCell => Tag::TableCell,
            original::Tag::Emphasis => Tag::Emphasis,
            original::Tag::Strong => Tag::Strong,
            original::Tag::Strikethrough => Tag::StrikeThrough,
            original::Tag::Link(link_type, destination_url, title) => Tag::Link((
                link_type.into(),
                destination_url.to_string(),
                title.to_string(),
            )),
            original::Tag::Image(link_type, destination_url, title) => Tag::Image((
                link_type.into(),
                destination_url.to_string(),
                title.to_string(),
            )),
        }
    }
}

impl<'a> From<original::Event<'a>> for Event {
    fn from(original_event: original::Event<'a>) -> Self {
        match original_event {
            original::Event::Start(tag) => Event::Start(tag.into()),
            original::Event::End(tag) => Event::End(tag.into()),
            original::Event::Text(cow_str) => Event::Text(cow_str.into_string()),
            original::Event::Code(cow_str) => Event::Code(cow_str.into_string()),
            original::Event::Html(cow_str) => Event::Html(cow_str.into_string()),
            original::Event::FootnoteReference(cow_str) => {
                Event::FootnoteReference(cow_str.into_string())
            }
            original::Event::SoftBreak => Event::SoftBreak,
            original::Event::HardBreak => Event::HardBreak,
            original::Event::Rule => Event::Rule,
            original::Event::TaskListMarker(tag) => Event::TaskListMarker(tag),
        }
    }
}

impl From<original::Options> for Options {
    fn from(op: original::Options) -> Self {
        let mut options = Options::empty();
        if op.contains(original::Options::ENABLE_TABLES) {
            options.insert(Options::ENABLE_TABLES);
        }
        if op.contains(original::Options::ENABLE_FOOTNOTES) {
            options.insert(Options::ENABLE_FOOTNOTES);
        }
        if op.contains(original::Options::ENABLE_STRIKETHROUGH) {
            options.insert(Options::ENABLE_STRIKETHROUGH);
        }
        if op.contains(original::Options::ENABLE_TASKLISTS) {
            options.insert(Options::ENABLE_TASKLISTS);
        }
        if op.contains(original::Options::ENABLE_SMART_PUNCTUATION) {
            options.insert(Options::ENABLE_SMART_PUNCTUATION);
        }
        if op.contains(original::Options::ENABLE_HEADING_ATTRIBUTES) {
            options.insert(Options::ENABLE_HEADING_ATTRIBUTES);
        }
        options
    }
}

impl From<Options> for original::Options {
    fn from(op: Options) -> Self {
        let mut options = original::Options::empty();
        if op.contains(Options::ENABLE_TABLES) {
            options.insert(original::Options::ENABLE_TABLES);
        }
        if op.contains(Options::ENABLE_FOOTNOTES) {
            options.insert(original::Options::ENABLE_FOOTNOTES);
        }
        if op.contains(Options::ENABLE_STRIKETHROUGH) {
            options.insert(original::Options::ENABLE_STRIKETHROUGH);
        }
        if op.contains(Options::ENABLE_TASKLISTS) {
            options.insert(original::Options::ENABLE_TASKLISTS);
        }
        if op.contains(Options::ENABLE_SMART_PUNCTUATION) {
            options.insert(original::Options::ENABLE_SMART_PUNCTUATION);
        }
        if op.contains(Options::ENABLE_HEADING_ATTRIBUTES) {
            options.insert(original::Options::ENABLE_HEADING_ATTRIBUTES);
        }
        options
    }
}

impl PartialEq<std::ops::Range<usize>> for pulldown::Range {
    fn eq(&self, other: &std::ops::Range<usize>) -> bool {
        self.start == other.start.try_into().unwrap() && self.end == other.end.try_into().unwrap()
    }
}

impl PartialEq<original::Event<'_>> for Event {
    fn eq(&self, other: &original::Event<'_>) -> bool {
        match (self, other) {
            (Self::Start(left), original::Event::Start(right)) => left == right,
            (Self::End(left), original::Event::End(right)) => left == right,
            (Self::Text(left), original::Event::Text(right)) => {
                left == &right.clone().into_string()
            }
            (Self::Code(left), original::Event::Code(right)) => {
                left == &right.clone().into_string()
            }
            (Self::Html(left), original::Event::Html(right)) => {
                left == &right.clone().into_string()
            }
            (Self::FootnoteReference(left), original::Event::FootnoteReference(right)) => {
                left == &**right
            }
            (Self::SoftBreak, original::Event::SoftBreak) => true,
            (Self::HardBreak, original::Event::HardBreak) => true,
            (Self::Rule, original::Event::Rule) => true,
            (Self::TaskListMarker(left), original::Event::TaskListMarker(right)) => left == right,
            _ => false,
        }
    }
}

impl PartialEq<original::Tag<'_>> for Tag {
    fn eq(&self, other: &original::Tag<'_>) -> bool {
        match (self, other) {
            (Self::Paragraph, original::Tag::Paragraph) => true,
            (
                Self::Heading(left),
                original::Tag::Heading(right_level, right_fragment_identifier, right_classes),
            ) => {
                left.0 == *right_level
                    && left.1 == right_fragment_identifier.map(str::to_string)
                    && left.2.iter().eq(right_classes)
            }
            (Self::BlockQuote, original::Tag::BlockQuote) => true,
            (Self::CodeBlock(left), original::Tag::CodeBlock(right)) => left == right,
            (Self::ListTag(left), original::Tag::List(right)) => left == right,
            (Self::Item, original::Tag::Item) => true,
            (Self::FootnoteDefinition(left), original::Tag::FootnoteDefinition(right)) => {
                left == &**right
            }
            (Self::Table(left), original::Tag::Table(right)) => left == right,
            (Self::TableHead, original::Tag::TableHead) => true,
            (Self::TableRow, original::Tag::TableRow) => true,
            (Self::TableCell, original::Tag::TableCell) => true,
            (Self::Emphasis, original::Tag::Emphasis) => true,
            (Self::Strong, original::Tag::Strong) => true,
            (Self::StrikeThrough, original::Tag::Strikethrough) => true,
            (
                Self::Link(left),
                original::Tag::Link(right_link_type, right_destination_url, right_title),
            ) => {
                left.0 == *right_link_type
                    && left.1 == **right_destination_url
                    && left.2 == **right_title
            }
            (
                Self::Image(left),
                original::Tag::Image(right_link_type, right_destination_url, right_title),
            ) => {
                left.0 == *right_link_type
                    && left.1 == **right_destination_url
                    && left.2 == **right_title
            }
            _ => false,
        }
    }
}

impl PartialEq<original::Alignment> for Alignment {
    fn eq(&self, other: &original::Alignment) -> bool {
        matches!(
            (self, other),
            (Alignment::None, original::Alignment::None)
                | (Alignment::Left, original::Alignment::Left)
                | (Alignment::Center, original::Alignment::Center)
                | (Alignment::Right, original::Alignment::Right)
        )
    }
}

impl PartialEq<original::LinkType> for LinkType {
    fn eq(&self, other: &original::LinkType) -> bool {
        matches!(
            (self, other),
            (LinkType::Inline, original::LinkType::Inline)
                | (LinkType::Reference, original::LinkType::Reference)
                | (
                    LinkType::ReferenceUnknown,
                    original::LinkType::ReferenceUnknown
                )
                | (LinkType::Collapsed, original::LinkType::Collapsed)
                | (
                    LinkType::CollapsedUnknown,
                    original::LinkType::CollapsedUnknown
                )
                | (LinkType::Shortcut, original::LinkType::Shortcut)
                | (
                    LinkType::ShortcutUnknown,
                    original::LinkType::ShortcutUnknown
                )
                | (LinkType::Autolink, original::LinkType::Autolink)
                | (LinkType::Email, original::LinkType::Email)
        )
    }
}

impl PartialEq<original::CodeBlockKind<'_>> for CodeBlockKind {
    fn eq(&self, other: &original::CodeBlockKind<'_>) -> bool {
        match (self, other) {
            (Self::Fenced(left), original::CodeBlockKind::Fenced(right)) => left == &**right,
            (Self::Indented, original::CodeBlockKind::Indented) => true,
            _ => false,
        }
    }
}

impl PartialEq<original::HeadingLevel> for HeadingLevel {
    fn eq(&self, other: &original::HeadingLevel) -> bool {
        matches!(
            (self, other),
            (HeadingLevel::H1, original::HeadingLevel::H1)
                | (HeadingLevel::H2, original::HeadingLevel::H2)
                | (HeadingLevel::H3, original::HeadingLevel::H3)
                | (HeadingLevel::H4, original::HeadingLevel::H4)
                | (HeadingLevel::H5, original::HeadingLevel::H5)
                | (HeadingLevel::H6, original::HeadingLevel::H6)
        )
    }
}

impl From<Range> for std::ops::Range<usize> {
    fn from(r: Range) -> Self {
        std::ops::Range {
            start: r
                .start
                .try_into()
                .expect("Conversion shouldn't never fail in practice"),
            end: r
                .end
                .try_into()
                .expect("Conversion shouldn't never fail in practice"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::pulldown::Pulldown as _;

    #[test]
    fn convert_markdown_to_html() {
        let markdown_str = r#"
hello
=====

* alpha
* beta
"#;

        let result = Pulldown::markdown_to_html(markdown_str.to_string());

        assert_eq!(
            result,
            r#"<h1>hello</h1>
<ul>
<li>alpha</li>
<li>beta</li>
</ul>
"#
        );
    }

    #[test]
    fn parser_with_option_strikethrough() {
        let markdown_input = "Hello world, this is a ~~complicated~~ *very simple* example.";

        let option = Options::ENABLE_STRIKETHROUGH;

        let iters: Vec<OffsetItem> =
            Pulldown::parse_with_options(markdown_input.to_string(), option);

        let expected: Vec<(original::Event, std::ops::Range<usize>)> =
            original::Parser::new_ext(markdown_input, option.into())
                .into_offset_iter()
                .collect();

        assert_eq!(iters.len(), expected.len());
        for (a, b) in iters.into_iter().zip(expected) {
            assert_eq!(a.0, b.0);
            assert_eq!(a.1, b.1);
        }
    }

    #[test]
    fn html_test_1() {
        let original = r##"Little header
<script type="text/js">
function some_func() {
console.log("teeeest");
}
function another_func() {
console.log("fooooo");
}
</script>"##;
        let expected = r##"<p>Little header</p>
<script type="text/js">
function some_func() {
console.log("teeeest");
}
function another_func() {
console.log("fooooo");
}
</script>"##;

        let result = Pulldown::markdown_to_html(original.to_string());
        assert_eq!(result, expected);
    }
}
