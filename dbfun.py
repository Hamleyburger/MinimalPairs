from application import db
from application.models import Word, Pair

Word.add("tudse")

#Pair.pair(word, word2, "kt")

print(Word.homonyms("tudse"))

if Word.homonyms("haletudse") is None:
    print("no such thing as haletudse")

db.session.commit()
