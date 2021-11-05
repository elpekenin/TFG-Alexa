import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename="app.log", filemode="w")

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import SkillBuilder
from flask_ask_sdk.skill_adapter import SkillAdapter
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
SKILL_ID = "amzn1.ask.skill.890dcdea-cae2-42fe-b34b-504e605f5b38"
skill_builder = SkillBuilder()

from flask import Flask, render_template, request
import json
PORT = 5000
app = Flask(__name__)

from pymongo import MongoClient
DATABASE_IP = "192.168.1.9"
DATABASE_NAME = "TFG"
database = MongoClient(DATABASE_IP)[DATABASE_NAME]

class BaseHandler(AbstractRequestHandler):
    amazon: bool = False
    def can_handle(self, handler_input) -> bool:
        return ask_utils.is_request_type(
            "AMAZON." * self.amazon + self.__class__.__name__.split("Handler")[0]
        )(handler_input)


class CustomHandler(AbstractRequestHandler):
    def can_handle(self, handler_input) -> bool:
        return ask_utils.is_intent_name(
            self.__class__.__name__.split("Handler")[0]
        )(handler_input)


class LaunchRequestHandler(BaseHandler):
    def handle(self, handler_input) -> Response:
        speak_output: str =  "Bienvenido a info uni; tengo información de asignaturas, profesores, horarios y mucho más. Que quieres hacer hoy?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class AsignaturaIntentHandler(CustomHandler):
    def handle(self, handler_input) -> Response:
        asignatura = ask_utils.request_util.get_slot(handler_input, "AsignaturaSlot").value
        speak_output: str =  f"Información de {asignatura}, okey"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask(speak_output)
                .response
        )


class HelpIntentHandler(BaseHandler):
    amazon: bool = True

    def handle(self, handler_input) -> Response:
        speak_output: str =  "Las opciones disponibles son: Asignatura, Horario, Profesor. Qué quieres consultar?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input) -> bool:
        return (
            ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
            ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)
        )

    def handle(self, handler_input) -> Response:
        speak_output: str =  "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class FallbackIntentHandler(BaseHandler):
    amazon: bool = True

    def handle(self, handler_input) -> Response:
        speech = "No estoy seguro. Puedes decir Ayuda para ver las opciones disponibles. Qué quieres hacer?"
        reprompt = "No te entendí. Con qué puedo ayudarte?"
        return handler_input.response_builder.speak(speech).ask(reprompt).response


class SessionEndedRequestHandler(BaseHandler):
    def handle(self, handler_input) -> Response:
        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    def can_handle(self, handler_input) -> bool:
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output: str =  f"Se ha activado el intent {intent_name}."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception) -> bool:
        return True

    def handle(self, handler_input, exception) -> Response:
        logger.error(exception, exc_info=True)

        speak_output: str =  "No pude hacer lo que has pedido, prueba de nuevo."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


skill_builder.add_request_handler(LaunchRequestHandler())
skill_builder.add_request_handler(AsignaturaIntentHandler())
skill_builder.add_request_handler(HelpIntentHandler())
skill_builder.add_request_handler(CancelOrStopIntentHandler())
skill_builder.add_request_handler(FallbackIntentHandler())
skill_builder.add_request_handler(SessionEndedRequestHandler()) 
#IntentReflectorHandler is last so it doesn't override other handlers
skill_builder.add_request_handler(IntentReflectorHandler())
skill_builder.add_exception_handler(CatchAllExceptionHandler())

skill_adapter = SkillAdapter(
    skill=skill_builder.create(),
    skill_id=SKILL_ID,
    app=app
)

@app.get("/")
def hello_world():
    return "Hello world!"

@app.post("/")
def invoke_skill():
    return skill_adapter.dispatch_request()

if __name__ == "__main__":
    pass   
