# Maps lowercase brand name variations → canonical display name.
# Add entries here whenever two sites use different names for the same brand.
# Keys must be lowercase; values are the display name shown in the UI.
# Changes here take effect on the next "Refresh Rates" click — no server restart needed.

ALIASES: dict[str, str] = {
    # Home Depot
    "the home depot":                           "Home Depot",
    "home depot":                               "Home Depot",
    "cheers to you (home depot)":               "Home Depot",

    # Walmart / Sam's Club
    "walmart/sam's club":                       "Walmart",
    "wal-mart":                                 "Walmart",
    "walmart":                                  "Walmart",
    "sam's club":                               "Sam's Club",

    # Amazon
    "amazon.com":                               "Amazon",
    "amazon":                                   "Amazon",

    # Airbnb
    "airbnb":                                   "Airbnb",
    "airbnb, inc.":                             "Airbnb",

    # adidas
    "adidas":                                   "adidas",

    # lululemon
    "lululemon":                                "lululemon",

    # GameStop
    "gamestop":                                 "GameStop",

    # Bass Pro Shops / Cabela's
    "bass pro shops":                           "Bass Pro Shops/Cabela's",
    "bass pro shops/cabela's":                  "Bass Pro Shops/Cabela's",

    # Foot Locker / Champs
    "foot locker":                              "Foot Locker/Champs",
    "foot locker/champs":                       "Foot Locker/Champs",

    # H-E-B
    "heb":                                      "H-E-B",
    "h-e-b":                                    "H-E-B",

    # Lowe's
    "lowe's":                                   "Lowe's",
    "lowes":                                    "Lowe's",

    # Macy's
    "macy's":                                   "Macy's",
    "macys":                                    "Macy's",

    # Marshalls / TJ Maxx
    "marshalls":                                "Marshalls/TJ Maxx/HomeGoods",
    "tj maxx":                                  "Marshalls/TJ Maxx/HomeGoods",
    "marshall's/tj maxx":                       "Marshalls/TJ Maxx/HomeGoods",
    "t.j maxx/marshall's":                      "Marshalls/TJ Maxx/HomeGoods",
    "t.j. maxx/marshalls/homegoods/sierra":     "Marshalls/TJ Maxx/HomeGoods",

    # Wayfair
    "wayfair":                                  "Wayfair",
    "wayfair.com":                              "Wayfair",

    # Athleta / Gap family
    "athleta":                                  "Gap/Old Navy/Athleta/Banana Republic",
    "gap":                                      "Gap/Old Navy/Athleta/Banana Republic",
    "old navy":                                 "Gap/Old Navy/Athleta/Banana Republic",
    "banana republic":                          "Gap/Old Navy/Athleta/Banana Republic",
    "athleta/gap/old navy/banana republic":     "Gap/Old Navy/Athleta/Banana Republic",
    "athleta/banana republic/gap/old navy":     "Gap/Old Navy/Athleta/Banana Republic",
    "athleta/banana republic/gap/old navy":     "Gap/Old Navy/Athleta/Banana Republic",

    # Academy Sports
    "academy sports + outdoors":                "Academy Sports",
    "academy sports":                           "Academy Sports",

    # Chewy
    "chewy":                                    "Chewy",
    "chewy.com":                                "Chewy",

    # DraftKings
    "draftkings":                               "DraftKings",
    "draft kings":                              "DraftKings",

    # Regal Cinemas
    "regal":                                    "Regal Cinemas",
    "regal cinemas":                            "Regal Cinemas",

    # Nordstrom
    "nordstrom":                                "Nordstrom",
    "nordstrom/rack":                           "Nordstrom",

    # Williams-Sonoma / West Elm / Pottery Barn
    "williams-sonoma":                          "Williams-Sonoma/West Elm/Pottery Barn",
    "williams sonoma/west elm/pottery barn":    "Williams-Sonoma/West Elm/Pottery Barn",

    # Uber
    "uber":                                     "Uber/UberEats",
    "uber/ubereats":                            "Uber/UberEats",
}
