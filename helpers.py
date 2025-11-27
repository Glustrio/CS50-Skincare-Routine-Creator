import requests

from flask import redirect, render_template, session
from functools import wraps

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def product_has_bad_ingredient(row, skin_type):
    bad_set = set(bad_ingredients_by_skin_type[skin_type])
    ingreds = set(row["clean_ingreds"])  # assuming already a list
    return len(bad_set & ingreds) > 0

def get_good_matches(ingredients, skin_type):
    return [i for i in ingredients if i in good_ingredients_by_skin_type[skin_type]]

def product_has_fragrance(row):
    bad_set = set(fragrance_ingredients)
    ingreds = set(row["clean_ingreds"])  # assuming already a list
    return len(bad_set & ingreds) > 0

bad_ingredients_by_skin_type = {
    "Oily": [
        # Occlusive / heavy, potentially pore-clogging oils & butters
        "petrolatum",
        "paraffinum liquidum",
        "lanolin",
        "lanolin alcohol",
        "cera alba",
        "microcrystalline wax",
        "ozokerite",
        "butyrospermum parkii",
        "garcinia indica seed butter",
        "shorea stenoptera butter",
        "coconut alkanes",
        "cocos nucifera fruit extract",
        "isopropyl myristate",
        "isopropyl palmitate",
        "isopropyl isostearate",
        "isostearyl isostearate",
        "isostearyl alcohol",
        "octyldodecanol",
        "isopropyl myristate",
        "myristyl myristate",

        # Heavy waxy esters / film formers
        "cetyl palmitate",
        "triacontanyl pvp",
        "polyethylene",
        "cera microcristallina",

        # Strong fragrance allergens (often problematic for acne-prone/oily)
        "parfum",
        "parfum of sandalwood",
        "parfum of vanilla",
        "aroma",
        "limonene",
        "linalool",
        "citronellol",
        "coumarin",
        "eugenol",
        "hexyl cinnamal",
        "benzyl salicylate",
        "benzyl benzoate",
        "butylphenyl methylpropional",
        "isoeugenol"
    ],

    "Dry": [
        # Drying / denatured alcohols
        "alcohol",
        "alcohol denat",
        "sd alcohol 40-a (alcohol denat)",
        "isopropyl alcohol",
        "ethanol",

        # Strong sulfates / harsh surfactants
        "sodium lauryl sulfate",
        "ammonium lauryl sulfate",
        "sodium laureth sulfate",
        "laureth sulfate",
        "magnesium laureth sulfate",
        "magnesium oleth sulfate",
        "sodium oleth sulfate",
        "tea-lauryl sulfate",
        "sodium lauroyl sarcosinate",
        "sodium lauryl sulfoacetate",

        # Astringent / potentially barrier-disrupting extracts
        "hamamelis virginiana",
        "hamamelis",
        "menthol",
        "camphor",
        "peppermint",
        "eucalyptus globulus",
        "mentha piperita extract",

        # Strong fragrance allergens (extra rough on dry/sensitive skin)
        "parfum",
        "parfum of sandalwood",
        "parfum of vanilla",
        "aroma",
        "limonene",
        "linalool",
        "citronellol",
        "coumarin",
        "eugenol",
        "cinnamal",
        "hydroxycitronellal",
        "hexyl cinnamal",
        "benzyl alcohol",
        "benzyl salicylate",
        "benzyl benzoate",
        "butylphenyl methylpropional",
        "isoeugenol"
    ],

    "Combination": [
        # Things that can both clog oily areas *and* irritate/dry out the rest
        "petrolatum",
        "paraffinum liquidum",
        "lanolin",
        "lanolin alcohol",
        "cera alba",
        "butyrospermum parkii",
        "coconut alkanes",
        "cocos nucifera fruit extract",
        "isopropyl myristate",
        "isopropyl palmitate",
        "isopropyl isostearate",
        "isostearyl isostearate",
        "myristyl myristate",

        # Harsh surfactants that can strip drier zones but be tempting in oily T-zone products
        "sodium lauryl sulfate",
        "ammonium lauryl sulfate",
        "sodium laureth sulfate",
        "laureth sulfate",
        "sodium lauryl sulfoacetate",

        # Strong actives that can be over-drying/irritating if layered badly
        "glycolic acid",
        "mandelic acid",
        "salicylic acid",
        "retinol",
        "retinyl palmitate",
        "retinal",
        "hydroxypinacolone retinoate",

        # Fragrance / essential oil allergens (common trigger for mixed skin)
        "parfum",
        "parfum of sandalwood",
        "parfum of vanilla",
        "aroma",
        "limonene",
        "linalool",
        "citronellol",
        "coumarin",
        "eugenol",
        "cinnamal",
        "benzyl alcohol",
        "benzyl salicylate",
        "benzyl benzoate",
        "butylphenyl methylpropional",
        "lavandula angustifolia",
        "citrus aurantium dulcis",
        "citrus limon juice extract",
        "citrus aurantium bergamia"
    ]
}

good_ingredients_by_skin_type = {
    "Oily": [
        # Best for oil control, congestion, acne, shine reduction
        "salicylic acid",
        "niacinamide",
        "zinc pca",
        "zinc oxide",
        "bentonite",
        "charcoal powder",
        "tea tree oil" ,

        # Lightweight humectants
        "glycerin",
        "sodium hyaluronate",
        "urea",
        "panthenol",
        "saccharide isomerate",
        "sodium pca",

        # Sebum-balancing botanicals
        "hamamelis virginiana",
        "camellia sinensis extract",
        "aloe barbadenis extract",
        "betula alba bark extract",
        "juniperus mexicana oil",
        "rosmarinus officinalis extract",
        "citrullus lanatus fruit extract",
        "hordeum vulgare extract",

        # Non-heavy emollients for moisture but not grease
        "squalene",
        "propylene glycol",
        "caprylyl glycol",
        "pentylene glycol",
        "butylene glycol"
    ],

    "Dry": [
        # Deep barrier support
        "ceramide np",
        "ceramide ap",
        "ceramide eop",
        "ceramide 1",
        "ceramide 3",
        "ceramide 6 ii",
        "cholesterol",

        # Strong humectant hydration
        "sodium hyaluronate",
        "hyaluronic acid",
        "glycerin",
        "urea",
        "sodium pca",
        "trehalose",
        "panthenol",
        "sorbitol",
        "betaine",
        "erythritol",
        "hydrolyzed sodium hyaluronate",
        "saccharide isomerate",

        # Emollient + moisturizing oils (safe for dry not oily)
        "squalene",
        "butyrospermum parkii",
        "olea europaea fruit oil",
        "helianthus annuus seed oil",
        "sesamium indicum seed oil",
        "cucumis sativus extract",
        "prunus amygdalus dulcis",
        "persea gratissima oil",
        "borago officinalis seed oil",
        "limnanthes alba seed oil",

        # Soothing + anti-inflammatory extracts
        "allantoin",
        "colloidal oatmeal",
        "aloe barbadenis extract",
        "centella asiatica extract",
        "glycyrrhiza glabra root extract",
        "chamomilla recutita flower oil",
        "calendula officinalis extract",
        "rosmarinus officinalis extract"
    ],

    "Combination": [
        # Balanced hydration without heaviness
        "niacinamide",
        "panthenol",
        "glycerin",
        "sodium hyaluronate",
        "trehalose",
        "urea",
        "betaine",
        "aloe barbadenis extract",
        "sodium pca",

        # Gentle exfoliation + pore maintenance without over-drying
        "salicylic acid",
        "glycolic acid",
        "mandelic acid",
        "lactic acid",

        # Lightweight oils / ceramides that moisturize dry zones without clogging oily
        "ceramide np",
        "ceramide ap",
        "ceramide eop",
        "ceramide 3",
        "ceramide 6 ii",
        "squalene",

        # Good botanical antioxidants
        "camellia sinensis extract",
        "betula alba bark extract",
        "centella asiatica extract",
        "glycyrrhiza glabra root extract",
        "rosmarinus officinalis extract",
        "saccharomyces lysate extract",
        "tremella fuciformis extract"
    ]
}

fragrance_ingredients = [
    'parfum', 
    'linalool', 
    'citronellol', 
    'limonene', 
    'coumarin', 
    'alpha-isomethyl ionone', 
    'geraniol', 
    'citral', 
    'benzyl alcohol', 
    'benzyl benzoate', 
    'hydroxycitronellal', 
    'hexyl cinnamal', 
    'benzyl salicylate', 
    'butylphenyl methylpropional', 
    'eugenol', 
    'isoeugenol', 
    'parfum of sandalwood', 
    'farnesol', 
    'zingiber aromaticus extract', 
    'ethyl 2,2-dimethylhydrocinnamal', 
    'cinnamyl alcohol', 
    'cinnamal', 
    'methyl eugenol', 
    'anisyl alcohol', 
    'amyl cinnamal', 
    'aroma', 
    'hexyl cinnamal eugenol', 
    'parfum of vanilla', 
    'pure plant parfum of vanilla', 
    'matthiola longipetala (night scented stock) seed oil', 
    'fluorescent brightener 230 salt', 
    'dichlorobenzyl alcohol', 
    'parfum of lime', 
    'hexyl cinnamal hydroycitronellal'
    ]