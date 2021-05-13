from flask import session
from markupsafe import Markup


def Content(locale=None):
    """ If you pass a locale in here session will be ignored """
    text_da = {
        "locale_code": "da",

        # Layout.html
        "title_all": "Minimale Par",
        "nav_find": "Find kontraster",
        "nav_collection": "Samling",
        "nav_language": "Sprog",
        "footer_copyright": "Copyright 2021 | <a href='https://github.com/Hamleyburger'>Alma Manley</a> | All Rights Reserved",

        # Front page
        "title_index": "Velkommen",
        "about": [
            "Minimale Par",
            ' <p> <i>Minimale par</i> er kort beskrevet par af ord, hvis betydning kun er adskilt af en enkelt lyd. </p>\
                Derfor er minimale par gode til at vise hvordan en lyd\
                kan være afgørende for den opfattede betydning af ordet. Hvis jeg for eksempel siger [d] når jeg mener [k], bliver "krage" til "drage", og\
                så har jeg pludselig en flok drager på taget.\
                <p> "Minimale Par" er en voksende database med ord, der danner par på kryds og tværs. \
                Indholdet er tilpasset brug i logopædisk praksis, hvor det kan anvendes i arbejdet med udtale og skelnen af danske sproglyde:\
                <dl>\
                <dt>Der sigtes efter ord, som er nemme at billedliggøre</dt>\
                    <dd>- "ko" og "løbe" er nemme at se for sig. Men hvordan viser man for eksempel "bruge" og "hensigt"?</dd>\
                <dt>Der kan tilføjes par, som ikke er ægte minimale par</dt>\
                    <dd>- "skyr" vs. "dyr" har mere end en enkelt lyd til forskel. Men parret er relevant til brug med elever, der erstatter [sg] med [d]</dd>\
                <dt>Der kan tilføjes par, som <i>kan</i> være minimale alt afhængigt af elevens udtale.</dt>\
                    <dd>- "ruder" vs. "guder", kan have [ʁ] og [g] til forskel, med mindre [u] udsættes for nok r-påvirkning til at lyde mere som [o].</dd>\
                </dl>\
                </p>\
                \
                <p>I siden <i>find kontraster</i> kan du søge på lyde med IPA-symboler og finde både minimale par og serier (multiple oppositioner). \
                Ordene kan tilføjes til en samling med <i class = "fas fa-plus-circle" > \
                </i> og fjernes med <i class ="fas fa-minus-circle"></i> \
                Fra siden <i>samling</i> kan du generere en PDF-fil, \
                som kan downloades og printes tosidet, så du får et billedmateriale med en bagside.w </p>'
        ],

        # Find contrasts
        "title_soundsearch": "Find kontraster",
        "url_soundsearch": "find-kontraster",
        "btn_sound": "lydsøgning",
        "tab_pairs": "Minimale par",
        "tab_MOs": "Multiple oppositioner",
        "IPA_description": "Marker tekstfeltet og tryk på et tegn for at indsætte",
        "btn_addall": "Tilføj alle",
        "btn_clearall": "Fjern alle",
        "exactmatch": "Resultater med alle lyde",
        "partialmatch": "Alternative forslag",
        "nomatches": "Ingen resultater",

        "tooltip_searchpairs": "søg efter minimale par",
        "tooltip_searchMOs": "søg efter multiple oppositioner",
        "tooltip_addresults": "føj alle resultater til samling",
        "tooltip_rmresults": "fjern alle resultater fra samling",
        "tooltip_wordinfo": "gå til ordets infoside",
        "tooltip_addword": "føj ord til samling",
        "tooltip_rmword": "fjern ord fra samling",
        "tooltip_addpair": "føj par til samling",
        "tooltip_rmpair": "fjern par fra samling",
        "tooltip_addMO": "føj MO-sæt til samling",
        "tooltip_rmMO": "fjern MO-sæt fra samling",

        # Collection
        "title_collection": "Samling",
        "url_collection": "samling",
        "tooltip_cleareall": "Ryd samling",
        "btn_makePDF": "Generer PDF",
        "collection_tip": 'Føj ord til samlingen med <i class="fas fa-plus-circle"></i> og fjern dem med <i class="fas fa-minus-circle"></i>',

        # Word info
        "title_wordinfo": "Info-om-ord",
        "url_wordinfo": "info-om-ord"
    }

    text_en = {
        "locale_code": "en",

        # Layout.html
        "title_all": "Minimal Pairs",
        "nav_find": "Find Contrasts",
        "nav_collection": "Collection",
        "nav_language": "Language",
        "footer_copyright": "Copyright 2021 | <a href='https://github.com/Hamleyburger'>Alma Manley</a> | All Rights Reserved",

        # Front page
        "title_index": "Home",
        "about": [
            "Out of words?",
            ' <p> "Minimale Par" (Danish for "minimal pairs") is a growing database of minimal pairs. \
                Here you can search and collect word pairs with images and generate \
                convenient two-sided PDF files for printing and using in \
                speech language therapy sessions or simply for practicing \
                phonological contrasts in the Danish language. </p> \
                <p> <i>"If you mean code but say this word: toad - I think of a \
                toad(shows a picture of a toad) </i> </p> \
                <p> Minimal pairs are technically word pairs differing only by \
                one sound in the same position in each word. \
                However in speech sound disorders it is common to have mislearned \
                phonological representations of clusters of sounds as well as isolated \
                sounds. Therefore "Minimale Par" also uses contrasts on a phonotactical \
                level - word pairs differing by clusters of sounds in the same positions.\
                 </p> <p> Additionally to word pairs it is possible to search for \
                "multiple opposition sets" - sets of words that are all distinguished \
                from each other by one sound(or cluster). Multiple opposition sets can \
                be used when a number of differend sounds are all replaced by the same \
                sounds. </p> <p> When you like a word use <i class = "fas fa-plus-circle" > \
                </i> to add it to your collection. Use <i class ="fas fa-minus-circle"></i> \
                to remove it again. </p>'
        ],

        # Find contrasts
        "title_soundsearch": "Sound search",
        "url_soundsearch": "sound-search",
        "btn_sound": "sound search",
        "tab_pairs": "Pairs",
        "tab_MOs": "Multiple oppositions",
        "IPA_description": "Marker boksen og tryk på et tegn for at indsætte",
        "btn_addall": "Add all",
        "btn_clearall": "Clear all",

        "tooltip_searchpairs": "search for minimal pairs",
        "tooltip_searchMOs": "search for multiple oppositions",
        "tooltip_addresults": "add all results to collection",
        "tooltip_rmresults": "remove all results from collection",
        "tooltip_wordinfo": "see word info",
        "tooltip_addword": "add word to collection",
        "tooltip_rmword": "remove word from collection",
        "tooltip_addpair": "add pair to collection",
        "tooltip_rmpair": "remove pair from collection",
        "tooltip_addMO": "add MO to collection",
        "tooltip_rmMO": "remove MO from collection",
        "exactmatch": "Exact matches",
        "partialmatch": "Partial matches",
        "nomatches": "No results",

        # Collection
        "title_collection": "Collection",
        "url_collection": "collection",
        "tooltip_cleareall": "clear collection",
        "btn_makePDF": "Make PDF",
        "collection_tip": 'Add words to your collection with <i class="fas fa-plus-circle"></i> and remove them with <i class="fas fa-minus-circle"></i>',

        # Word info
        "title_wordinfo": "Word-info",
        "url_wordinfo": "word-info"

    }

    if locale == None:
        locale = session["locale"]

    if locale == "en":
        return text_en
    else:
        return text_da


da_content = Content("da")
en_content = Content("en")