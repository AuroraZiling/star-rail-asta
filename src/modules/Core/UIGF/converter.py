def originalToUIGFListUnit(original, uigfGachaType):
    return {"gacha_type": original["gacha_type"],
            "gacha_id": original["gacha_id"],
            "item_id": original["item_id"],
            "count": original["count"],
            "time": original["time"],
            "name": original["name"],
            "item_type": original["item_type"],
            "rank_type": original["rank_type"],
            "id": original["id"],
            "uigf_gacha_type": uigfGachaType}
