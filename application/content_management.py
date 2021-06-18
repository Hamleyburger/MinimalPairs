from flask import session
from markupsafe import Markup
from .content_management_meta import meta_en, meta_da


def Content(locale=None):
    """ If you pass a locale in here session will be ignored """

    text_da = {

        # Cross page
        "locale_code": "da",
        "btn_clearall": "Fjern alle",
        "tooltip_help": "Hjælp",
        "close": "Luk",

        # Layout.html
        "title_all": "Minimale Par",
        "nav_find": "Find kontraster",
        "nav_collection": "Samling",
        "nav_language": "Sprog",
        "footer_copyright": "Copyright 2021 | <a href='https://github.com/Hamleyburger'>Alma Manley</a> | All Rights Reserved",


        # Front page
        "title_index": "Velkommen",
        "about": [
            "Velkommen til minimalepar.dk",
            ' <p><i>Minimale par</i> er kort beskrevet par af ord, hvis betydning kun er adskilt af en enkelt lyd. </p>\
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
        "exactmatch": "Resultater med alle lyde",
        "partialmatch": "Alternative forslag",
        "nomatches": "Ingen resultater",

        "help_soundsearch_cue": "Indtast mållyde",
        "help_pairs_title": "Søg efter minimale par",
        "help_pairs_content": '\
            <p>Søg efter sæt med minimale par ved at indsætte mållydene i søgefelterne. Du kan også indsætte konsonantklynger.</p>\
            <p>Hvis du ikke har IPA-tegnet på dit keyboard, kan du klikke i det felt, du vil indsætte et tegn i, og bagefter klikke på tegnet i tegnvælgeren.</p>\
            <p>Du kan bruge bindestreg <span class="texthighlight">-</span> til at søge efter udeladte lyde - f.eks. "sø" vs. "ø" med udeladelse af [s].</p>\
            <p>Du kan bruge asterisk <span class="texthighlight">*</span> til at søge efter "alle lyde" - f.eks. [s] vs. "*" for at finde alle par med [s].</p>\
            <p>I resultaterne kan du tilføje et ord til din samling med <i class = "fas fa-plus-circle"></i> og fjerne det med <i class ="fas fa-minus-circle"></i>. </p>\
            ',
        "help_MO_title": "Søg efter sæt med multiple oppositioner",
        "help_MO_content": '\
            <p>Søg efter sæt med multiple oppositioner ved at indsætte mållydene i søgefelterne.</p>\
            <p>Hvis du ikke har IPA-tegnet på dit keyboard, kan du klikke i det felt, du vil indsætte et tegn i, og bagefter klikke på tegnet i tegnvælgeren.</p>\
            <p>Alle felterne behøver ikke være fyldt ud, men det øverste felt må ikke stå tomt. En “tom” lyd kan skrives med et minus “-“, så “ø” over for “sø” er “-“ over for “s”.</p>\
            <p>I resultaterne kan du tilføje et ord til din samling med <i class = "fas fa-plus-circle"></i> og fjerne det med <i class ="fas fa-minus-circle"></i>. </p>\
            ',

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

        # Word info
        "title_wordinfo": "info om ",  # set word.word in template
        "url_wordinfo": "info-om-ord",

        # Collection
        "title_collection": "Samling",
        "url_collection": "samling",
        "tooltip_cleareall": "Ryd samling",
        "btn_PDFtool": "PDF-værktøj",
        "btn_makePDF": "Generer PDF",
        "collection_tip": 'Føj ord til samlingen med <i class="fas fa-plus-circle"></i> og fjern dem med <i class="fas fa-minus-circle"></i>',
        "help_pdf_cue": "Vælg bagside yadda yadda",
        "help_pdf_title": "Generer PDF-fil med bagside",
        "help_pdf_content": '\
            <p>Generer en PDF-fil med ordkort med alle ordene i din samling. Kortene kan bruges til f.eks. at spille vendespil eller fisk.</p>\
            <p>PDF-filen er beregnet til at blive printet to-sidet, således at hveranden side har et mønster, som vil blive printet på bagsiden af hvert ark med ordkort.</p>\
            <p>Ved at trykke på “generer PDF”, vil du blive videresendt til en side, hvor du kan vælge at gemme filen på din enhed.</p>\
            ',

        # Backside image names
        # actual files must be svg for source (static/permaimages) and png for thumbnail (static/permaimages/thumbnails/_thumb*)
        "bs_label_fishcookies": "Fiskekager",
        "bs_filename_fishcookies": "fiskpattern",

        "bs_label_logocat": "Logokatte",
        "bs_filename_logocat": "catpattern",

        # Rendered PDF
        "title_pdf": "Ordkort"

    }

    text_en = {

        # Cross page
        "locale_code": "en",
        "btn_clearall": "Clear all",
        "tooltip_help": "Help",
        "close": "Close",

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
        "IPA_description": "Select an input field and click a symbol to insert",
        "btn_addall": "Add all",
        "exactmatch": "Exact matches",
        "partialmatch": "Partial matches",
        "nomatches": "No results",


        "help_soundsearch_cue": "Insert target sounds",
        "help_pairs_title": "Search for minimal pairs",
        "help_pairs_content": '\
            <p>Search for minimal pairs by inserting the target sounds in the search fields. You can also insert consonant clusters.</p>\
            <p>If you’re missing a symbol your keyboard you can insert it by first selecting a search field and then selecting the symbol in the IPA symbol picker.</p>\
            <p> In the results use <i class = "fas fa-plus-circle"></i> to add a word to your collection. Use <i class ="fas fa-minus-circle"></i> to remove it. </p>\
            ',
        "help_MO_title": "Search for multiple opposition sets",
        "help_MO_content": '\
            <p>Search for multiple opposition sets by inserting the target sounds in the search fields.</p>\
            <p>If you’re missing a symbol your keyboard you can insert it by first selecting a search field and then selecting the symbol in the IPA symbol picker.</p>\
            <p>Some search fields can be left empty, but there must be a sound in the top field. An “empty” sound can be written with a minus “-“, so “ø” against “sø” would be “-“ against “s”.</p>\
            <p> In the results use <i class = "fas fa-plus-circle"></i> to add a word to your collection. Use <i class ="fas fa-minus-circle"></i> to remove it. </p>\
            ',

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

        # Word info
        "title_wordinfo": "info about ",  # set word.word in template
        "url_wordinfo": "word-info",

        # Collection
        "title_collection": "Collection",
        "url_collection": "collection",
        "tooltip_cleareall": "clear collection",
        "btn_PDFtool": "PDF tool",
        "btn_makePDF": "Make PDF",
        "collection_tip": 'Add words to your collection with <i class="fas fa-plus-circle"></i> and remove them with <i class="fas fa-minus-circle"></i>',
        "help_pdf_cue": "Choose a back design",
        "help_pdf_title": "Generate a PDF file with a back design",
        "help_pdf_content": '\
            <p>Generate a PDF file with word cards for all the words in your collection. The cards can be used for playing Memory, for example, or Go Fish.</p>\
            <p>The PDF is meant for double-sided printing so that each sheet with word cards will have a design printed on its back.</p>\
            <p>By clicking "Generate PDF”, you will be redirected to a page where you will have the option of saving the file.</p>\
            ',



        # Backside image names
        # actual files must be svg for source (static/permaimages) and png for thumbnail (static/permaimages/thumbnails/_thumb*)
        "bs_label_fishcookies": "Fish cookies",
        "bs_filename_fishcookies": "fiskpattern",

        "bs_label_logocat": "Logo cats",
        "bs_filename_logocat": "catpattern",

        # Rendered PDF
        "title_pdf": "Word cards"
    }

    text_da.update(meta_da)
    text_en.update(meta_en)

    if locale == None:
        locale = session["locale"]

    if locale == "en":
        return text_en
    else:
        return text_da


da_content = Content("da")
en_content = Content("en")
