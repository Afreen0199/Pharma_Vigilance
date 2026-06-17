import spacy
import scispacy

print("spacy version:", spacy.__version__)
print("scispacy version:", scispacy.__version__)

try:
    nlp = spacy.load("en_core_sci_md")
    doc = nlp("Myeloid derived suppressor cells (MDSC) are immature myeloid cells.")
    print("Entities:", doc.ents)
    print("SUCCESS: SciSpacy model loaded and ran successfully!")
except Exception as e:
    print("ERROR loading SciSpacy model:", e)
