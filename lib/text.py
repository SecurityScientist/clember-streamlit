from random import randint


def adjust_lang(text):
    def _replace_should(text, capitalize=False, shoulds=["organizations should", "organisations should"], alternatives=["you could", "you can", "you may"]):
        for organizations_should in shoulds:
            if capitalize is True:
                organizations_should = organizations_should.capitalize()

            if organizations_should in text:
                alternative = alternatives[randint(0, len(alternatives) - 1)]
                if capitalize is True:
                    alternative = alternative.capitalize()

                text = text.replace(organizations_should, alternative)
                text = text.replace("their", "")
        return text

    for boolean in [True, False]:
        text = _replace_should(text, capitalize=boolean, shoulds=["organizations should", "organisations should"], alternatives=["you could", "you can", "you may"])
        text = _replace_should(text, capitalize=boolean, shoulds=["should organizations", "should organisations"], alternatives=["could you", "can you"])
        text = _replace_should(text, capitalize=boolean, shoulds=["organizations need", "organisations need"], alternatives=["you could", "you can", "you may"])

    text = text.replace("should", "could")
    text = text.replace("must", "may")

    return text
