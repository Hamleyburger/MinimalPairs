from flask import session, g
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
        "nav_donation": "Støtte",
        "nav_language": "Sprog",
        "latest_news": "Nyeste tilføjelser",
        "news_added": "Tilføjet",
        "footer_copyright": "Copyright 2021 | <a href='https://github.com/Hamleyburger'>Alma Manley</a> | All Rights Reserved",


        # Front page
        "title_index": "Velkommen",
        "about": [
            "En database af minimale par",
            ' <p><i>Minimale par</i> er kort beskrevet par af ord, hvis betydning kun er adskilt af en enkelt lyd.\
                Derfor er minimale par gode til at vise hvordan en lyd\
                kan være afgørende for et ords betydning. Hvis jeg for eksempel erstatter [k] med [d], bliver "krage" til "drage", og\
                så har jeg pludselig en flok drager på taget.</p>\
                <p> "Minimale Par" er en voksende database med ord og billeder, der danner par på kryds og tværs. \
                Indholdet er tilpasset brug i logopædisk praksis. Det vil sige, at:\
                <ul>\
                <li>Materialet er ikke videnskabeligt akkurat - ordparrene er tilføjet et af gangen efter behov, baseret på en kvalitativ vurdering</li>\
                <li>Der sigtes efter ord, som er relativt nemme at billedliggøre</li>\
                <li>Der kan tilføjes par, som ikke er ægte minimale par på fonemniveau</li>\
                    <i><dd>F.eks. "skyr" vs. "dyr" har mere end en enkelt lyd til forskel. Men parret er relevant til brug med elever, der erstatter [sg] med [d]</dd></i>\
                <li>Der kan tilføjes par, som <i>kan</i> være minimale alt afhængigt af hvordan man udtaler dem.</li>\
                     <i><dd>"ruder" vs. "guder", kan have [ʁ] og [g] til forskel, med mindre [u] udsættes for nok r-påvirkning til at lyde mere som [o]. Så ville "ruder" i stedet danne [ʁ g]-par med "goder".</dd> </i>\
                <li>Der kan tilføjes ord, som bare er tæt nok på hinanden til at de kan bruges i praksis.</li>\
                     <i><dd>"Rist" og "hest" minder nok om hinanden til at man kan bruge dem, selv om vokalkvaliteten ikke er helt den samme.</dd> </i>\
                </ul>\
                </p>\
                \
                <p>På siden <i>find kontraster</i> kan du foretage en lydsøgning med IPA-symboler og finde både minimale par og multiple oppositioner. \
                Ordene kan tilføjes til en samling med <i class = "fas fa-plus-circle" > \
                </i> og fjernes med <i class ="fas fa-minus-circle"></i> \
                Fra siden <i>samling</i> kan du tilføje de billeder, der mangler, dublere ord og generere en PDF-fil, \
                som kan downloades og printes tosidet, så du får et billedmateriale med en bagside. </p>'
        ],

        # Find contrasts
        "title_soundsearch": "Find kontraster",
        "subtitle_soundsearch": "Find minimale par ved at søge på lyde",
        "subtitle_soundsearch_MO": "Find multiple oppositioner ved at søge på lyde",
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
        "artist_wordinfo": "Tegner",
        "url_wordinfo": "info-om-ord",
        "group_name": "Gruppe",

        # Collection
        "title_collection": "Samling",
        "url_collection": "samling",
        "tooltip_cleareall": "Ryd samling",
        "btn_PDFtool": "PDF-værktøj",
        "btn_makePDF": "Hent ordkort",
        "btn_makePDF_loading_text": "Arbejder",
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
        "pdf_game_btn": "Design et spil",
        "step1": "Trin 1",
        "step2": "Trin 2",
        "step3": "Trin 3",
        "step1_txt": "Vælg design",
        "step2_txt": "Arranger rækkefølge",
        "step3_txt": "Generer PDF",

        # Collection - board game themes:
        "board_game_info": [
            {
                "data_design":"solar",
                "description":"Terningspil med solsystemet. Max 30 billeder",
                "src": "permaimages/thumbnails/thumb_solarsystemboardgame.png"
            },
            {
                "data_design":"lottery-4",
                "description":"Billedlotteri med fire 2x2-plader. Bedst med 16 forskellige billeder",
                "src": "permaimages/thumbnails/thumb_lottery-4-boardgame.png"
            },                                                                                                                                                                                                                                                        
            {
                "data_design":"lottery-6",
                "description":"Billedlotteri med fire 2x3-plader. Bedst med 24 forskellige billeder",
                "src": "permaimages/thumbnails/thumb_lot6.jpg"
            }
        ],




        # Rendered PDF
        "title_pdf": "Ordkort",
        "missing_custom_image": "Brugerdefinerede billeder slettes efter noget tid. Hvis billedet mangler, så prøv at uploade billedet igen: ",


        # Stripe checkout
        "title_checkout": "Støtte",
        "title_thankyou": "1000 tak!",
        "text_thankyou": "Det er takket være mennesker som dig, at minimalepar.dk har et sted at bo.",
        "text_notthankyou": "Øredøvende tavshed...",
        "title_cancelled": "Anulleret",
        "donation_text": "Minimalepar.dk er et enkeltmandsprojekt udviklet, tegnet og vedligeholdt i min fritid. Ved at donere, hjælper du til med at dække en del af omkostningerne (server, domæne mv.). Du skal på ingen måde føle dig forpligtet til at donere - men jeg er ekstremt taknemmelig for enhver støtte.",
        "paypal_donation_link": "https://www.paypal.com/donate/?hosted_button_id=725GUDGS7PG5Q",

    
        # Contact
        "title_contact": "Kontakt",
        "form_label_name": "Navn",
        "form_label_email": "Email",
        "form_label_message": "Besked",
        "form_label_agree": 'Jeg accepterer, at denne formular er beskyttet af <a target=”_blank” href="https://support.google.com/recaptcha/answer/6080904?hl=en">reCaptcha</a>, og at minimalepar.dk får min emailadresse udelukkende med henblik på at kunne svare. Emailadressen og eventuelle personoplysninger i beskeden slettes efter højest et år.',
        "form_label_submit": "Send",
        "introtext_contact": '<p class="mb-1">Har du ris, ros, spørgsmål eller forslag? Opdaget en fejl på siden? Savner du kontraster eller billeder? Jeg vil rigtig gerne høre fra dig, så jeg kan finde op og ned på min to do-liste.</p><p>~ Alma fra minimalepar.dk</p>',


        # Error messsages
        "double_sound_error": "Man kan ikke søge på dobbeltlyde (to ens lyde) i et felt. Måske søgte du efter noget, der skrives med dobbeltkonsonant ortografisk, men faktisk udtales som en enkelt lyd?",
        "double_wc_error": "Man kan desværre ikke søge på * vs. * (alting vs. alting), da søgningen er for stor. Venligst indsæt en lyd i mindst et af felterne.",
        "wc_in_string_error": "\"*\" kan kun bruges alene, når du vil finde alle minimale par med én lyd. F.eks. [s] over for \"alt\"",
        "MO_wc_error": "Man kan ikke bruge wildcard (*) i en søgning efter multiple oppositioner. Prøv med enkeltlyde og konsonantklynger",
        "double_dash_error": "Man kan ikke søge på - over for -, fordi det er ingenting over for ingenting.",
        "dash_in_string_error": "\"-\" kan kun bruges alene, når du vil søge efter par, hvor en lyd udelades. F.eks. [s] over for \"ikke noget [s]\"",
        "syllable_structure_error": "Man kan kun søge på enkeltlyde eller konsonantklynger. Har du f.eks. søgt på 'kage' vs. 'smage', så prøv i stedet [k] vs. [sm]",
        "multi_syllable_error": "Man kan kun søge på enkeltlyde eller konsonantklynger. Prøv at lade vokallyde eller stavelsesbærende konsonantlyde stå alene.",
        "invalid_ipa_error": 'Der er søgt på noget, som søgemaskinen ikke kan fortolke som en lyd. Prøv at finde den lyd, du vil søge efter i tegnvælgeren. Hvis du har opdaget en fejl, så send meget gerne en besked fra kontaktsiden.',
        "too_few_oppositions_error": "Der skal som minimum indsættes lyde i det øverste felt og to af felterne til kontrastlyde.",
        "same_sound_error": "Søgningen fejlede, fordi der er søgt på to ens kontrastlyde.",
        "pair_data_required_error": "Begge felter skal udfyldes.",
        "unknown_or_csrf_error": "Noget gik galt. Måske hjælper det at genindlæse siden.",
        "no_result_message": [
            "Hvis du synes, at der mangler par med ",
            "så send gerne en besked og eventuelle forslag fra",
            "kontaktsiden"
            ],


    }

    text_en = {

        # Cross page
        "locale_code": "en",
        "btn_clearall": "Clear all",
        "tooltip_help": "Help",
        "close": "Close",

        # Layout.html
        "title_all": "Minimale Par",
        "nav_find": "Find Contrasts",
        "nav_collection": "Collection",
        "nav_donation": "Donate",
        "nav_language": "Language",
        "latest_news": "Latest additions",
        "news_added": "Added",
        "footer_copyright": "Copyright 2021 | <a href='https://github.com/Hamleyburger'>Alma Manley</a> | All Rights Reserved",

        # Front page
        "title_index": "Home",
        "about": [
            'A database of "minimale par"',
            ' <p> "Minimale Par" (Danish for "minimal pairs") is a growing database of minimal pairs. \
                Here you can search and collect word pairs with images and generate \
                convenient two-sided PDF files for printing and using in \
                speech language therapy sessions or simply for practicing \
                phonological contrasts in the Danish language. </p> \
                <p> <i>If you mean "code" but say "tode" - I think of a \
                toad (here\'s a picture of a toad) </i> </p> \
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
        "subtitle_soundsearch": "Find minimal pairs using sound search",
        "subtitle_soundsearch_MO": "Find multiple oppositions using sound search",
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
        "artist_wordinfo": "Illustrator",
        "url_wordinfo": "word-info",
        "group_name": "Group",

        # Collection
        "title_collection": "Collection",
        "url_collection": "collection",
        "tooltip_cleareall": "clear collection",
        "btn_PDFtool": "PDF tool",
        "btn_makePDF": "Download word cards",
        "btn_makePDF_loading_text": "Please wait",
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
        "pdf_game_btn": "Design a game",
        "step1": "Step 1",
        "step2": "Step 2",
        "step3": "Step 3",
        "step1_txt": "Select a theme",
        "step2_txt": "Order words",
        "step3_txt": "Generate PDF",


        # Collection - board game themes:
        "board_game_info": [
            {
                "data_design":"solar",
                "description":"Solar system themed dice game. 30 images max",
                "src": "permaimages/thumbnails/thumb_solarsystemboardgame.png"
            },
            {
                "data_design":"lottery-4",
                "description":"Image lottery with four two by two boards. Best with 16 different images",
                "src": "permaimages/thumbnails/thumb_lottery-4-boardgame.png"
            },
            {
                "data_design":"lottery-6",
                "description":"Image lottery with four two by three boards. Best with 24 different images",
                "src": "permaimages/thumbnails/thumb_lot6.jpg"
            }
        ],



        # Rendered PDF
        "title_pdf": "Word cards",
        "missing_custom_image": "Custom images are removed from the server after a while. If the image is missing try uploading it again: ",


        # Stripe checkout
        "title_checkout": "Support",
        "title_thankyou": "Thanks so much!",
        "text_thankyou": "Thanks to people like you minimalepar.dk can continue to exist.",
        "text_notthankyou": "Abysmal silence..",
        "title_cancelled": "Cancelled",
        "donation_text": "Minimalepar.dk is a one-man project developed, drawn and maintained in my free time. With your donation you will help cover the costs (server, domain etc.). You must not feel obliged in any way to donate, but I am extremely grateful for any support.",
        "paypal_donation_link": "https://www.paypal.com/donate/?hosted_button_id=725GUDGS7PG5Q",


        # Contact
        "title_contact": "Contact",
        "form_label_name": "Name",
        "form_label_email": "Email",
        "form_label_message": "Message",
        "form_label_agree": "I accept that this form is protected by <a target=”_blank” href='https://support.google.com/recaptcha/answer/6080904?hl=en'>reCaptcha</a> and that minimalepar.dk stores my email address with the sole purpose of replying. My email and any personal data in the message will be deleted within a year.",
        "form_label_submit": "Send",
        "introtext_contact": '<p class="mb-1">Do you have constructive criticism, questions, comments? Discovered an error on the site? Please write me a message and I\'ll try to get back to you as soon as possible.</p><p>~ Alma from minimalepar.dk</p>',


        # Error messsages
        "double_sound_error": "Searching for double sounds (two sounds of a kind) is not possible. Maybe you meant to search for something that is written ortographically with double consonants, but is actually pronounced as one sound?",
        "double_wc_error": "Searching for * vs. * is not possible because everything vs. everything is just too much data. Please insert at least one sound in one of the fields.",
        "MO_wc_error": "Wild card (*) cannot be used in searches for multiple oppositions. Please use single sounds or consonant clusters.",
        "double_dash_error": "Searching for - vs. - is not possible because it means nothing vs. nothing.",
        "dash_in_string_error": "\"-\" can only be used alone to search for pairs where one sound is omitted. Fx [s] vs. \"no [s]\"",
        "wc_in_string_error": "\"*\" can only be used alone to search for a sound and all its contrasts. Fx [s] vs. \"everything\"",
        "syllable_structure_error": "Only searches for single sounds or consonant clusters are possible. Fx if you have searched for 'kage' vs. 'smage', then try instead to search for [k] vs. [sm]",
        "multi_syllable_error": "Only searches for single sounds or consonant clusters are possible. Vowels and syllabic consonants must stand alone.",
        "invalid_ipa_error": 'The search engine received an input that it cannot recognize as a sound. Try finding the sound you want in the IPA symbol picker. If you have found an error please send a message from the contact page.',
        "too_few_oppositions_error": "As a minimum the field on top and two of the contrast fields must be filled out.",
        "same_sound_error": "The search failed because the same sound was typed twice.",
        "pair_data_required_error": "Both fields need to be filled out.",
        "unknown_or_csrf_error": "Something went wrong. It may help to reload the page.",
        "no_result_message": [
            "If you're missing pairs with ",
            "send a message and any suggestions through",
            "the contact page"
            ],


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
