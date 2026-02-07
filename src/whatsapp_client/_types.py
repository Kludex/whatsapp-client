from __future__ import annotations

from dataclasses import dataclass
from typing import Union


# --- Response types ---


@dataclass(frozen=True, slots=True, kw_only=True)
class Contact:
    input: str
    wa_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class MessageId:
    id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class MessageResponse:
    messaging_product: str
    contacts: list[Contact]
    messages: list[MessageId]


# --- Contact message types ---


@dataclass(frozen=True, slots=True, kw_only=True)
class ContactName:
    formatted_name: str
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    suffix: str | None = None
    prefix: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ContactPhone:
    phone: str
    type: str = "CELL"
    wa_id: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ContactEmail:
    email: str
    type: str = "WORK"


@dataclass(frozen=True, slots=True, kw_only=True)
class ContactAddress:
    street: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None
    country: str | None = None
    country_code: str | None = None
    type: str = "HOME"


@dataclass(frozen=True, slots=True, kw_only=True)
class ContactUrl:
    url: str
    type: str = "WORK"


@dataclass(frozen=True, slots=True, kw_only=True)
class ContactOrg:
    company: str | None = None
    department: str | None = None
    title: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ContactInfo:
    name: ContactName
    phones: list[ContactPhone] | None = None
    emails: list[ContactEmail] | None = None
    addresses: list[ContactAddress] | None = None
    urls: list[ContactUrl] | None = None
    org: ContactOrg | None = None
    birthday: str | None = None


# --- Template types ---


@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateTextParameter:
    text: str


@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateImageParameter:
    link: str


@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateVideoParameter:
    link: str


@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateDocumentParameter:
    link: str
    filename: str | None = None


TemplateParameter = Union[
    TemplateTextParameter, TemplateImageParameter, TemplateVideoParameter, TemplateDocumentParameter
]


@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateHeaderComponent:
    parameters: list[TemplateParameter]


@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateBodyComponent:
    parameters: list[TemplateParameter]


@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateButtonComponent:
    sub_type: str
    index: int
    parameters: list[TemplateParameter]


TemplateComponent = Union[TemplateHeaderComponent, TemplateBodyComponent, TemplateButtonComponent]


@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateLanguage:
    code: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Template:
    name: str
    language: TemplateLanguage
    components: list[TemplateComponent] | None = None


# --- Interactive types ---


@dataclass(frozen=True, slots=True, kw_only=True)
class ReplyButton:
    id: str
    title: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ListRow:
    id: str
    title: str
    description: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ListSection:
    title: str
    rows: list[ListRow]
