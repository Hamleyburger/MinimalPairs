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
        "description": "På \'find kontrster\' kan du søge med IPA-alfabetet og finde minimale par og multiple oppositioner, der kan tilføjes til din samling.",
        "og_description": "Find lydkontraster ved at søge på IPA-tegn",
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

        "og_image_width": "1000",
        "og_image_height": "1000",
    },

}


meta_en = {

    "layout": {

        # Layout (if nothing else is provided)
        "description": "layout description",
        "og_description": "ogdescription",
        "og_image": "",
        "og_image_secure_url": "",
        "og_image_alt": "",
        "og_title": "",
        "og_url": "",
        "og_image_type": "",
        "og_image_width": "",
        "og_image_height": "",
        "og_type": "",
        "og_site_name": "",
        "og_locale": "",
        "og_locale_alternate": ""

    },
    "contrasts": {

        # Layout (if nothing else is provided)
        "description": "layout description",
        "og_description": "ogdescription",
        "og_image": "",
        "og_image_secure_url": "",
        "og_image_alt": "",
        "og_title": "",
        "og_url": "",
        "og_image_type": "",
        "og_image_width": "",
        "og_image_height": "",
        "og_type": "",
        "og_site_name": "",
        "og_locale": "",
        "og_locale_alternate": ""

    },

}
print(meta_da["collection_meta"]["description"])
print("loaded content")
