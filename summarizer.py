import os

import nltk
import openai

if not os.getenv("API_KEY"):
    raise Exception("Setup API_KEY as environment variables!")

openai.api_key = os.getenv("API_KEY")
ENGINE = os.getenv("ENGINE", "text-davinci-003")

TLDR_POSTFIX = "\n tl;dr:"
SUMMARIZE_PREFIX = "Summarize this for an expert:\n\n"


def summarize(input_text, max_length=60):
    gpt3_prompt = SUMMARIZE_PREFIX + input_text + TLDR_POSTFIX
    response = openai.Completion.create(
        engine=ENGINE,
        prompt=gpt3_prompt,
        temperature=0.7,
        max_tokens=max_length,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    batch_summary = response["choices"][0]["text"]
    return post_processing(batch_summary)


def generate_summary(input_text, batch_size=512, max_length=140):
    sentences = nltk.tokenize.sent_tokenize(input_text)

    tokens = 0
    batch_sentence = ""
    batches = []
    for sentence in sentences:
        tokens = tokens + len(nltk.word_tokenize(sentence))
        if tokens <= batch_size:
            batch_sentence = batch_sentence + sentence
        else:
            batches.append(batch_sentence)
            batch_sentence = sentence
            tokens = len(nltk.word_tokenize(sentence))
    if batch_sentence not in batches:
        batches.append(batch_sentence)

    summary = ""
    for batch in batches:
        response = summarize(batch, max_length)
        summary = summary + str(response)
    return summary


def post_processing(response_text):
    # Incomplete sentence removal - splice until last index of fullstop
    try:
        fullstop_index = response_text.rindex(".")
        response_text = response_text[: fullstop_index + 1]
    except Exception as e:
        print(e)
    return response_text.replace("\\n", "")
