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
                kan være afgørende for et ords betydning. Hvis jeg for eksempel erstatter [k] med [d], bliver "krage" til "drage", og\
                så har jeg pludselig en flok drager på taget.\
                <p> "Minimale Par" er en voksende database med ord og (nogle) billeder, der danner par på kryds og tværs. \
                <dl>\
                <dt>Indholdet er tilpasset brug i logopædisk praksis</dt>\
                    <dd>Materialet er ikke videnskabeligt akkurat - ordparrene er tilføjet et af gangen efter behov, baseret på en kvalitativ vurdering</dd>\
                <dt>Der sigtes efter ord, som er relativt nemme at billedliggøre</dt>\
                    <dd>"ko" og "løbe" er nemme at se for sig. Men hvordan tegner man for eksempel "puds" (pudse i bydeform) og "hensigt" på en måde så børn har en change for at huske dem?</dd>\
                <dt>Der kan tilføjes par, som ikke er ægte minimale par på fonemniveau</dt>\
                    <dd>"skyr" vs. "dyr" har mere end en enkelt lyd til forskel. Men parret er relevant til brug med elever, der erstatter [sg] med [d]</dd>\
                <dt>Der kan tilføjes par, som <i>kan</i> være minimale alt afhængigt af elevens udtale.</dt>\
                    <dd>"ruder" vs. "guder", kan have [ʁ] og [g] til forskel, med mindre [u] udsættes for nok r-påvirkning til at lyde mere som [o]. Så ville "ruder" i stedet danne [ʁ g]-par med "goder". </dd>\
                </dl>\
                </p>\
                \
                <p>I siden <i>find kontraster</i> kan du søge på lyde med IPA-symboler og finde både minimale par og serier (multiple oppositioner). \
                Ordene kan tilføjes til en samling med <i class = "fas fa-plus-circle" > \
                </i> og fjernes med <i class ="fas fa-minus-circle"></i> \
                Fra siden <i>samling</i> kan du tilføje de billeder, der mangler, dublere ord og generere en PDF-fil, \
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
            <p>Søg efter ordpar ved at indsætte mållydene i søgefelterne. Du kan også indsætte konsonantklynger.</p>\
            <p>Hvis du ikke har IPA-tegnet på dit keyboard, kan du klikke i det felt, du vil indsætte et tegn i, og bagefter klikke på tegnet i tegnvælgeren.</p>\
            <p>Du kan bruge bindestreg <span class="texthighlight">-</span> til at søge efter "tomme" lyde - f.eks. "sø" vs. "ø" med udeladelse af [s].</p>\
            <p>Du kan bruge asterisk <span class="texthighlight">*</span> til at søge efter "alle lyde" - f.eks. [s] vs. "*" for at finde alle minimale par med [s].</p>\
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
        "tooltip_dupeword": "tilføj flere af samme ord",
        "tooltip_addpair": "føj par til samling",
        "tooltip_rmpair": "fjern par fra samling",
        "tooltip_addMO": "føj MO-sæt til samling",
        "tooltip_rmMO": "fjern MO-sæt fra samling",

        # Word info
        "title_wordinfo": "info om ",  # set word.word in template
        "url_wordinfo": "info-om-ord",
        "group_name": "Gruppe",

        # Collection
        "title_collection": "Samling",
        "url_collection": "samling",
        "tooltip_cleareall": "Ryd samling",
        "btn_PDFtool": "PDF-værktøj",
        "btn_makePDF": "Hent ordkort",
        "btn_make_game_board": 'Hent spilleplade',
        "collection_tip": 'Føj ord til samlingen med <i class="fas fa-plus-circle"></i> og fjern dem med <i class="fas fa-minus-circle"></i>',
        "help_pdf_cue": "Guide til PDF-værktøj",
        "help_pdf_title": "Generer PDF-fil med bagside",
        "help_pdf_content": '\
            <p>Generer en PDF-fil med alle ordene i din samling. Hvis ordet ikke har et billede, kan du tilføje dit eget ved at trykke på <i class="fas fa-upload"></i>, og hvis du vil have det samme ord flere gange, kan du dublere det med <i class="fas fa-clone"></i></p>\
            <p>Ordkortene med bagside er beregnet til at blive printet to-sidet, så hver anden side er et mønster.</p>\
            <p>Tryk på PDF-knapperne <i class="fas fa-file-pdf"></i> for at generere det valgte design.</p>\
            ',
        "help_pdf_choose_back": "Ordkort - vælg bagsidedekoration",
        "help_pdf_board_game": "Spilleplade - vælg design",

        # Backside image names
        # actual files must be svg for source (static/permaimages) and png for thumbnail (static/permaimages/thumbnails/_thumb*)
        "bs_label_fishcookies": "Fiskekager",
        "bs_filename_fishcookies": "fiskpattern",

        "bs_label_logocat": "Logokatte",
        "bs_filename_logocat": "catpattern",

        # Rendered PDF
        "title_pdf": "Ordkort",
        "missing_custom_image": "Brugerdefinerede billeder slettes efter noget tid. Hvis billedet mangler, så prøv at uploade billedet igen: ",

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
            "Welcome to minimalepar.dk",
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
                from each other by one sound (or cluster). Multiple opposition sets can \
                be used when a number of different sounds are all replaced by the same \
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
        "tooltip_dupeword": "duplicate word in collection",
        "tooltip_addpair": "add pair to collection",
        "tooltip_rmpair": "remove pair from collection",
        "tooltip_addMO": "add MO to collection",
        "tooltip_rmMO": "remove MO from collection",

        # Word info
        "title_wordinfo": "info about ",  # set word.word in template
        "url_wordinfo": "word-info",
        "group_name": "Group",

        # Collection
        "title_collection": "Collection",
        "url_collection": "collection",
        "tooltip_cleareall": "clear collection",
        "btn_PDFtool": "PDF tool",
        "btn_makePDF": "Download word cards",
        "btn_make_game_board": 'Download game board',
        "collection_tip": 'Add words to your collection with <i class="fas fa-plus-circle"></i> and remove them with <i class="fas fa-minus-circle"></i>',
        "help_pdf_cue": "Guide to PDF tool",
        "help_pdf_title": "Generate a PDF file with a back design",
        "help_pdf_content": '\
            <p>Generate a PDF file with all the words in your collection. If a word does not have an image you can add your own with <i class="fas fa-upload"></i>, and if you want more of the same word you can duplicate words with <i class="fas fa-clone"></i></p>\
            <p>The word cards with back decorations are meant for double-sided printing so that each sheet with word cards will have a design printed on its back.</p>\
            <p>Click the PDF buttons <i class="fas fa-file-pdf"></i> to generate a PDF with your chosen design.</p>\
            ',
        "help_pdf_choose_back": "Word cards - choose deoration on back",
        "help_pdf_board_game": "Game board - choose design",



        # Backside image names
        # actual files must be svg for source (static/permaimages) and png for thumbnail (static/permaimages/thumbnails/_thumb*)
        "bs_label_fishcookies": "Fish cookies",
        "bs_filename_fishcookies": "fiskpattern",

        "bs_label_logocat": "Logo cats",
        "bs_filename_logocat": "catpattern",

        # Rendered PDF
        "title_pdf": "Word cards",
        "missing_custom_image": "Custom images are removed from the server after a while. If the image is missing try uploading it again: ",
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
