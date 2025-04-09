from brunns.matchers.utils import append_matcher_description, describe_field_match, describe_field_mismatch
from hamcrest import anything
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.description import Description
from hamcrest.core.helpers.wrap_matcher import wrap_matcher


class AutoMatcherMeta(type):
    def __new__(cls, name, bases, namespace, **_kwargs):
        if name == "BaseAutoMatcher":
            return super().__new__(cls, name, bases, namespace)

        domain_class = namespace.get("__domain_class__")
        if domain_class is None:
            msg = f"{name} must define __domain_class__"
            raise TypeError(msg)

        for field_name in domain_class.__annotations__:
            attr_name = f"{field_name}_" if field_name in {"id", "type"} else field_name
            namespace[attr_name] = anything()

        return super().__new__(cls, name, bases, namespace)


class BaseAutoMatcher(BaseMatcher, metaclass=AutoMatcherMeta):
    __domain_class__ = None  # must be overridden

    def __init__(self):
        super().__init__()

    def describe_to(self, description: Description) -> None:
        description.append_text(f"{self.__class__.__name__.removesuffix('Matcher')} with")
        for field_name in self.__domain_class__.__annotations__:
            attr_name = f"{field_name}_" if field_name in {"id", "type"} else field_name
            append_matcher_description(getattr(self, attr_name), field_name, description)

    def _matches(self, item) -> bool:
        return all(
            getattr(self, f"{field}_" if field in {"id", "type"} else field).matches(getattr(item, field))
            for field in self.__domain_class__.__annotations__
        )

    def describe_mismatch(self, item, mismatch_description: Description) -> None:
        mismatch_description.append_text(f"was {self.__domain_class__.__name__} with")
        for field_name in self.__domain_class__.__annotations__:
            value = getattr(item, field_name)
            matcher = getattr(self, f"{field_name}_" if field_name in {"id", "type"} else field_name)
            describe_field_mismatch(matcher, field_name, value, mismatch_description)

    def describe_match(self, item, match_description: Description) -> None:
        match_description.append_text(f"was {self.__domain_class__.__name__} with")
        for field_name in self.__domain_class__.__annotations__:
            value = getattr(item, field_name)
            matcher = getattr(self, f"{field_name}_" if field_name in {"id", "type"} else field_name)
            describe_field_match(matcher, field_name, value, match_description)

    def __getattr__(self, name: str):
        if name.startswith(("with_", "and_")):
            base = name.removeprefix("with_").removeprefix("and_")
            attr = f"{base}_" if base in {"id", "type"} else base
            if hasattr(self, attr):

                def setter(value):
                    setattr(self, attr, wrap_matcher(value))
                    return self

                return setter
        msg = f"{type(self).__name__} object has no attribute {name}"
        raise AttributeError(msg)
