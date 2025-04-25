# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_intent_name, get_slot_value

from ask_sdk_model import Response
from backends.kitchenowl import KitchenOwlAPI
import os
import yaml
from ask_sdk_core.utils import get_locale

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
kitchenapi = KitchenOwlAPI(os.getenv("KITCHENOWL_HOUSEHOLD_ID"))
was_opened = False


LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locales')

def load_locale_strings(locale):
    """Loads strings for the given locale, falls back to en-US if locale not found."""
    locale_file_path = os.path.join(LOCALE_DIR, f'{locale}.yaml')
    if not os.path.exists(locale_file_path):
        # Fallback to default locale if the specific locale file doesn't exist
        print(f"Warning: Locale file not found for {locale}. Falling back to en-US.")
        locale_file_path = os.path.join(LOCALE_DIR, 'en-US.yaml') # Define your default locale

    try:
        with open(locale_file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading locale file {locale_file_path}: {e}")
        # In case of error, load the default locale's strings
        default_locale_file_path = os.path.join(LOCALE_DIR, 'en-US.yaml')
        with open(default_locale_file_path, 'r', encoding='utf-8') as f:
             return yaml.safe_load(f)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        global was_opened
        MSGS = load_locale_strings(get_locale(handler_input))
        # type: (HandlerInput) -> Response
        speak_output = MSGS['WELCOME']
        was_opened = True

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class AddItemHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AddItemIntent")(handler_input)

    def handle(self, handler_input):
        global was_opened
        MSGS = load_locale_strings(get_locale(handler_input))
        # type: (HandlerInput) -> Response
        item = get_slot_value(handler_input, "item")
        item = item.capitalize() if item else item

        if kitchenapi.check_item(item):
            msg = MSGS["ITEM_EXISTS"].format(item)
            if was_opened:
                msg += MSGS["ANYTHING"]
        else:
            result = kitchenapi.add_item(item)
            if result.status_code == 200:
                msg = MSGS["ITEM_ADDED"].format(item)
                if was_opened:
                    msg += MSGS["ANYTHING"]
            else:
                logger.error(MSGS["FAILED_ADDING"].format(result.status_code, result.text))
                msg = MSGS["WRONG"]

        rb = handler_input.response_builder.speak(msg)
        if was_opened:
            rb = rb.ask(MSGS["ANYTHING"])

        return rb.response


class ListItemsHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ListItemsIntent")(handler_input)

    def handle(self, handler_input):
        global was_opened
        MSGS = load_locale_strings(get_locale(handler_input))
        items = kitchenapi.list_items()

        num_items = len(items)
        if num_items == 0:
            msg = MSGS["LIST_EMPTY"]
        elif num_items == 1:
            msg = MSGS["LIST_ONEITEM"].format(items[0])
        else:
            item_list = ", ".join(items[0:-1]) + MSGS["AND"] + items[-1]
            msg = MSGS["LIST_ITEMS"].format(len(items), item_list)

        rb = handler_input.response_builder.speak(msg)

        if was_opened:
            rb = rb.ask(MSGS["ANYTHING"])

        return rb.response


# class ClearItemsHandler(AbstractRequestHandler):
#     def can_handle(self, handler_input):
#         return ask_utils.is_intent_name("ClearItemsIntent")(handler_input)
#
#     def handle(self, handler_input):
#         MSGS = load_locale_strings(get_locale(handler_input))
#         try:
#             result = kitchenapi.clear_items()
#             msg = MSGS["LIST_CLEARED"]
#         except Exception:
#             msg = MSGS["WRONG"]
#
#         rb =  handler_input.response_builder.speak(msg)
#         if was_opened:
#             rb.ask(MSGS["ANYTHING"])
#
#         return rb.response


class RemoveItemHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("RemoveItemIntent")(handler_input)

    def handle(self, handler_input):
        global was_opened
        item_name = get_slot_value(handler_input, "item")
        item_name = item_name.capitalize() if item_name else item_name
        MSGS = load_locale_strings(get_locale(handler_input))

        try:
            result = kitchenapi.remove_item(item_name)
            if len(result) == 0:
                msg = MSGS["ITEM_NOT_FOUND"].format(item_name)
                if was_opened:
                    msg += " Anything else?"
            elif all(r.status_code == 200 for r in result):
                msg = MSGS["ITEM_REMOVED"].format(item_name)
                if was_opened:
                    msg += MSGS["ANYTHING"]
            else:
                msg = MSGS["ITEM_REMOVED_PARTIAL"].format(item_name)
                if was_opened:
                    msg += MSGS["ANYTHING"]
        except Exception:
            msg = MSGS["WRONG"]

        rb = handler_input.response_builder.speak(msg)
        if was_opened:
            rb.ask(MSGS["ANYTHING"])

        return rb.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        MSGS = load_locale_strings(get_locale(handler_input))
        speak_output = MSGS["HELP_OPTIONS"]

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel, No and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input)
            or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)
            or ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        MSGS = load_locale_strings(get_locale(handler_input))
        speak_output = MSGS["BYE"]

        return handler_input.response_builder.speak(speak_output).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        global was_opened

        was_opened = False

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder.speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        MSGS = load_locale_strings(get_locale(handler_input))
        speak_output = MSGS["TROUBLE"]

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AddItemHandler())
sb.add_request_handler(ListItemsHandler())
sb.add_request_handler(RemoveItemHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(
    IntentReflectorHandler()
)  # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

handler = sb.lambda_handler()
