from flask import url_for


meta_da = {

    "layout": {

        # Layout (if nothing else is provided) will use page specific content from 'index'
        # "description"
        # "og_description"
        # "og_image"
        # "og_image_alt"
        # "og_title"
        # husk at sætte url i template

        # The below content is shown on all pages
        "og_image_type": "image/jpeg",
        "og_image_width": "1200",
        "og_image_height": "1200",
        "og_type": "website",
        "og_site_name": "minimalepar.dk",
        "og_locale": "da_DK",
        "og_locale_alternate": "en_GB"

    },
    "index": {

        "description": "Velkommen til minimalepar.dk. Søg efter lyde og find minimale par og multiple oppositioner med billeder. Lav ark med ordkort som PDF, der kan printes.",
        "og_description": "En voksende database med minimale par og multiple oppositioner",
        "og_image": "permaimages/og/ogfrontpage.jpg",  # Just the path to the image
        "og_image_alt": "Forsideillustration med en kat, en hat, en sol og en stol",
        "og_title": "Velkommen til minimalepar.dk",
        # husk at sætte url i template
        # uses default image type, width and height from layout

    },
    "contrasts": {

        # Layout (if nothing else is provided)
        "description": "På \'find kontrster\' kan du søge på lyde med IPA-tegn og finde minimale par og multiple oppositioner, der kan bruges til at lave ord- og billedmaterialer.",
        "og_description": "Find minimale par ved at søge på IPA-tegn",
        "og_image": "permaimages/og/ogfindkontraster.jpg",  # Just the path to the image
        "og_image_alt": "Illustration til siden 'find kontraster'",
        "og_title": "Find kontraster",
        # husk at sætte url i template
        # uses default image type, width and height from layout

    },
    "collection_meta": {

        # Layout (if nothing else is provided)
        "description": "Når du har samlet de ord, du vil have, kan du se dem i din samling og lave en PDF-fil, der kan printes tosidet og bruges som ordkort med bagside.",
        "og_description": "Lav en PDF-fil med ordkort ud fra de ord, du har valgt.",
        "og_image": "permaimages/og/ogsamling.jpg",  # Just the path to the image
        "og_image_alt": "Illustration til siden 'samling'",
        "og_title": "Min samling",
        # husk at sætte url i template
        # uses default image type, width and height from layout

    },
    "wordinfo": {

        # Layout (if nothing else is provided)
        # add word in template
        "description": "Se, hvordan ordet danner minimale par eller multiple oppositioner med andre ord",
        "og_description": "Information om kontraster til ordet ",  # add word.word in template
        # "og_image": set in template
        "og_image_alt": "Billede af ",  # set word.word in template
        "og_title": "Info om ordet ",  # set word.word in template
        # husk at sætte url i template

        "og_image_width": "400",
        "og_image_height": "400",
    },

}


meta_en = {

    "layout": {

        # Layout (if nothing else is provided) will use page specific content from 'index'
        # "description"
        # "og_description"
        # "og_image"
        # "og_image_alt"
        # "og_title"
        # husk at sætte url i template

        # The below content is shown on all pages
        "og_image_type": "image/jpeg",
        "og_image_width": "1200",
        "og_image_height": "1200",
        "og_type": "website",
        "og_site_name": "minimalepar.dk",
        "og_locale": "en_GB",
        "og_locale_alternate": "da_DK"

    },
    "index": {

        "description": "Welcome to minimalepar.dk. Find Danish minimal pairs by performing a sound search and turn your collection of words into a two-sided PDF.",
        "og_description": "A growing database with Danish minimal pairs",
        "og_image": "permaimages/og/ogfrontpage.jpg",  # Just the path to the image
        "og_image_alt": "Front page illustration with a cat with a hat, a sun and a chair",
        "og_title": "Welcome to minimalepar.dk",
        # husk at sætte url i template
        # uses default image type, width and height from layout

    },
    "contrasts": {

        # Layout (if nothing else is provided)
        "description": "In \'sound search\' you can search with IPA-symbols and find Danish minimal pairs and add them to your collection.",
        "og_description": "Find contrasting words with an IPA sound search",
        "og_image": "permaimages/og/ogfindkontraster.jpg",  # Just the path to the image
        "og_image_alt": "Illustration with the minimalpar cat and word card examples",
        "og_title": "Sound search",
        # husk at sætte url i template
        # uses default image type, width and height from layout

    },
    "collection_meta": {

        # Layout (if nothing else is provided)
        "description": "View the words in your collection and create a PDF with word cards that can be printed two-sided.",
        "og_description": "Create a PDF with word cards from the words you have collected",
        "og_image": "permaimages/og/ogsamling.jpg",  # Just the path to the image
        "og_image_alt": "Illustration with the minimalpar cat an word card examples with back designs",
        "og_title": "My collection",
        # husk at sætte url i template
        # uses default image type, width and height from layout

    },
    "wordinfo": {

        # Layout (if nothing else is provided)
        # add word in template
        "description": "Se how the word relates to other words in the database",
        "og_title": "Info about ",  # set word.word in template
        # add word.word in template
        "og_description": "See minimal contrasts and opposition sets for the word ",
        # "og_image": set in template
        "og_image_alt": "Image of ",  # set word.word in template
        # husk at sætte url i template

        "og_image_width": "400",
        "og_image_height": "400",
    },

}
