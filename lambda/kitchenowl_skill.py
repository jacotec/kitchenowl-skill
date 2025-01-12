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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
kitchenapi = KitchenOwlAPI(os.getenv("KITCHENOWL_HOUSEHOLD_ID"))
was_opened = False


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        global was_opened
        # type: (HandlerInput) -> Response
        speak_output = "This is Kitchen Owl. What would you like to do?"
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
        # type: (HandlerInput) -> Response
        item = get_slot_value(handler_input, "item")
        item = item.capitalize() if item else item

        result = kitchenapi.add_item(item)
        if result.status_code == 200:
            msg = f"I have added {item}."
            if was_opened:
                msg += " Anything else?"
        else:
            logger.error(f"Failed adding: {result.status_code}: {result.text}")
            msg = "Something went wrong."

        rb = handler_input.response_builder.speak(msg)
        if was_opened:
            rb = rb.ask("Anything else? ")

        return rb.response


class ListItemsHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ListItemsIntent")(handler_input)

    def handle(self, handler_input):
        global was_opened
        items = kitchenapi.list_items()

        num_items = len(items)
        if num_items == 0:
            msg = "Your shopping list is empty."
        elif num_items == 1:
            msg = f"There is one item on your list: {items[0]}"
        else:
            item_list = ", ".join(items[0:-1]) + " and " + items[-1]
            msg = f"You have {len(items)} items on the list: {item_list}"

        rb = handler_input.response_builder.speak(msg)

        if was_opened:
            rb = rb.ask("Anything else? ")

        return rb.response


# class ClearItemsHandler(AbstractRequestHandler):
#     def can_handle(self, handler_input):
#         return ask_utils.is_intent_name("ClearItemsIntent")(handler_input)
#
#     def handle(self, handler_input):
#
#         try:
#             result = kitchenapi.clear_items()
#             msg = "List cleared."
#         except Exception:
#             msg = "Something went wrong."
#
#         rb =  handler_input.response_builder.speak(msg)
#         if was_opened:
#             rb.ask("Anything else?")
#
#         return rb.response


class RemoveItemHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("RemoveItemIntent")(handler_input)

    def handle(self, handler_input):
        global was_opened
        item_name = get_slot_value(handler_input, "item")

        try:
            result = kitchenapi.remove_item(item_name)
            if all(r.status_code == 200 for r in result):
                msg = f"Removed {item_name} from the shopping list."
            else:
                msg = f"Partial success removing {item_name} from the shopping list."
        except Exception:
            msg = "Something went wrong."

        rb = handler_input.response_builder.speak(msg)
        if was_opened:
            rb.ask("Anything else?")

        return rb.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say 'add coca-cola', \"what's on my list or 'remove potatoes'"

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
        speak_output = "Bye!"

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

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

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
