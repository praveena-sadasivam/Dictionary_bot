from flask import Flask,render_template,request,jsonify
from nltk.corpus import wordnet as word_net
from logging.handlers import RotatingFileHandler
from spellchecker import SpellChecker

spell = SpellChecker()


#flask object
app=Flask(__name__,
template_folder="template",
static_folder="static")

file_handler = RotatingFileHandler("error.log", maxBytes=1024 * 1024 * 100)
app.logger.addHandler(file_handler)


@app.errorhandler(500)
def handle_500_error(exception):
    app.logger.error(exception)
    return "Internal Server Error"

@app.errorhandler(404)
def handle_404_error(exception):
    app.logger.error(exception)
    return "Not Found"

@app.route("/")
def get_html():
    print("\nopening web page\n")
    return render_template("bot.html")

@app.route("/api/reply",methods=['GET'])
def get_reply():
    #declaration
    synonym = set()
    antonym = set()
    misspelled=[]
    synonyms = " "
    antonyms = " "
    suggestion=" "

    #getting user input
    word = request.args.get("word")
    print("user input: ",word)

    misspelled=spell.unknown([word])
    for syn in word_net.synsets(word):
        for item in syn.lemmas():
            synonym.add(item.name())
            if item.antonyms():
                antonym.add(item.antonyms()[0].name())
    
    synonym = list(synonym)
    antonym = list(antonym)

    #SYNONYMS
    if len(synonym):
        for item in synonym:
            if item is synonym[-1]:
                synonyms+=' '+item+'.'
            else:
                synonyms+=' '+item+', '
    else:
         synonyms="NIL"
    print("\ngetting synonyms\n")

    #ANTONYMS
    if len(antonym):
        for item in antonym:
            if item is antonym[-1]:
                antonyms+=' '+item+'.'
            else:
                antonyms+=' '+item+', '
    else:
        antonyms="NIL"
    print("\ngetting antonyms\n")

    #MEANING
    if word in word_net.all_lemma_names():
        syn = word_net.synsets(word)[0]
        meaning=syn.definition()
    else:
        meaning="NIL"
    print("\ngetting meaning\n")

    #SUGGESTIONS
    if len(misspelled):
        for word in misspelled:
            suggest=list(spell.candidates(word))
            print("\ngetting suggestions\n")
            for item in suggest:
                if item in word_net.all_lemma_names():
                    if item is suggest[-1]:
                        suggestion+=' '+item+'.'
                    else:
                        suggestion+=' '+item+', '
        
        return jsonify(suggestion)
    else:
        return jsonify([meaning,synonyms,antonyms])


if __name__ == '__main__':
    app.run(debug=True,port=3000)
