import json
from google.cloud import dialogflow
from environs import Env


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    """Create an intent of the given intent type."""
    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        # Here we create a new training phrase for each provided part.
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name, training_phrases=training_phrases, messages=[message]
    )

    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )

    print("Intent created: {}".format(response))


def main():
    env = Env()
    env.read_env()
    project_id = env.str('PROJECT_ID')
    intents_to_learn = env.str('NEW_INTENTS_FILE_PATH')

    with open(intents_to_learn) as f:
        intents = f.read()
        intents_decoded = json.loads(intents)

    for intense, response in intents_decoded.items():

        training_phrases_parts = [
            question for question in response['questions']
        ]

        create_intent(
            project_id=project_id,
            display_name=intense,
            training_phrases_parts=training_phrases_parts,
            message_texts=[response['answer']]
        )


if __name__ == '__main__':
    main()
