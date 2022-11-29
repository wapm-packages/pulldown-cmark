use std::ops::Range;

use crate::pulldown::{
    Alignment, CodeBlockKind, CowStr, Error, Event, HeadingLevel, LinkType, OffsetItem, Options,
    Tag,
};

use ::pulldown_cmark as original;

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
            .map(|offset_item| (offset_item.0.into(), offset_item.1.into()))
            .collect()
    }

    fn parse_with_options(markdown: String, options: Options) -> Vec<OffsetItem> {
        original::Parser::new_ext(&markdown, options.into())
            .into_offset_iter()
            .map(|offset_item| (offset_item.0.into(), offset_item.1.into()))
            .collect()
    }
}

impl From<Range<usize>> for pulldown::Range {
    fn from(r: Range<usize>) -> Self {
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
