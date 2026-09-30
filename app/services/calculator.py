def calculate_account_value(player: dict) -> dict:
    # 1. 전투 실력 및 승리 점수
    trophies = player.get("trophies", 0)
    highest = player.get("highestTrophies", trophies)
    v_3vs3 = player.get("3vs3Victories", 0)
    v_solo = player.get("soloVictories", 0)
    v_duo = player.get("duoVictories", 0)

    # 랭커일수록 승수와 트로피 가중치 체감 극대화
    trophy_score = trophies * 1.8
    highest_bonus = max(0, (highest - trophies)) * 0.6
    victory_score = (v_3vs3 * 18) + ((v_solo + v_duo) * 12)
    battle_total = int(trophy_score + highest_bonus + victory_score)

    # 2. 브롤러 육성 점수
    brawlers = player.get("brawlers", [])
    brawler_count_score = len(brawlers) * 800

    power_score = 0
    gadget_score = 0
    sp_score = 0
    gear_score = 0
    max_brawlers = 0

    total_gadgets = 0
    total_sps = 0
    total_gears = 0

    for b in brawlers:
        p = b.get("power", 1)
        # 11레벨(만렙) 소모 재화 가중치
        if p == 11:
            power_score += 2800
            max_brawlers += 1
        elif p == 10:
            power_score += 1600
        elif p == 9:
            power_score += 850
        else:
            power_score += p * 60

        g_count = len(b.get("gadgets", []))
        sp_count = len(b.get("starPowers", []))
        gear_count = len(b.get("gears", []))

        total_gadgets += g_count
        total_sps += sp_count
        total_gears += gear_count

        gadget_score += g_count * 350
        sp_score += sp_count * 700
        gear_score += gear_count * 400

    progression_total = int(brawler_count_score + power_score + gadget_score + sp_score + gear_score)
    total_score = battle_total + progression_total

    # 3. 재화 및 원화 환산
    estimated_gold = int(total_score * 0.88)
    estimated_krw = int(total_score * 0.42)

    # 4. 66만점 = 상위 20% 기준 현실화된 10단계 랭크 시스템
    if total_score >= 1200000:
        tier = "ULTIMATE"
        tier_kr = "얼티밋"
        percentile = "상위 0.01% 월드 클래스"
        tier_style = "bg-gradient-to-r from-red-600/30 to-amber-600/30 border-amber-400 text-amber-300 shadow-[0_0_25px_rgba(251,191,36,0.4)]"
    elif total_score >= 1000000:
        tier = "CHALLENGER"
        tier_kr = "챌린저"
        percentile = "상위 0.1% 천상계 랭커"
        tier_style = "bg-gradient-to-r from-cyan-600/30 to-blue-600/30 border-cyan-400 text-cyan-300 shadow-[0_0_20px_rgba(34,211,238,0.35)]"
    elif total_score >= 850000:
        tier = "GRANDMASTER"
        tier_kr = "그랜드마스터"
        percentile = "상위 1% 최정상"
        tier_style = "bg-purple-950/70 border-purple-400 text-purple-300 shadow-[0_0_20px_rgba(192,132,252,0.3)]"
    elif total_score >= 750000:
        tier = "MASTER"
        tier_kr = "마스터"
        percentile = "상위 5% 초고수"
        tier_style = "bg-fuchsia-950/60 border-fuchsia-500 text-fuchsia-300"
    elif total_score >= 680000:
        tier = "LEGENDARY"
        tier_kr = "전설"
        percentile = "상위 12% 고수"
        tier_style = "bg-red-950/60 border-red-500 text-red-300"
    elif total_score >= 580000:
        tier = "MYTHIC"
        tier_kr = "신화"
        percentile = "상위 20% 숙련자"
        tier_style = "bg-emerald-950/60 border-emerald-500 text-emerald-300"
    elif total_score >= 420000:
        tier = "DIAMOND"
        tier_kr = "다이아몬드"
        percentile = "상위 35% 중상위권"
        tier_style = "bg-sky-950/60 border-sky-400 text-sky-300"
    elif total_score >= 260000:
        tier = "GOLD"
        tier_kr = "골드"
        percentile = "상위 55% 일반"
        tier_style = "bg-amber-950/60 border-amber-400 text-amber-300"
    elif total_score >= 120000:
        tier = "SILVER"
        tier_kr = "실버"
        percentile = "상위 75% 입문자"
        tier_style = "bg-slate-900 border-slate-500 text-slate-300"
    else:
        tier = "BRONZE"
        tier_kr = "브론즈"
        percentile = "하위 25% 뉴비"
        tier_style = "bg-amber-950/20 border-amber-800 text-amber-600"

    return {
        "total_score": total_score,
        "tier": tier,
        "tier_kr": tier_kr,
        "percentile": percentile,
        "tier_style": tier_style,
        "estimated_gold": estimated_gold,
        "estimated_krw": estimated_krw,
        "breakdown": {
            "battle_total": battle_total,
            "progression_total": progression_total,
            "brawler_count": len(brawlers),
            "max_brawlers": max_brawlers,
            "gadget_count": total_gadgets,
            "sp_count": total_sps,
            "gear_count": total_gears,
        },
    }