# =============================================================================
# SISTEMA DE LEADERBOARD - Rankings de Jogadores
# =============================================================================

@bot.command()
async def top(ctx, categoria: str = None):
    """
    Sistema de Leaderboard - Rankings de jogadores
    
    Uso:
        !top - Menu com todas as categorias
        !top kills - Top 10 matadores
        !top kd - Top 10 K/D ratio
        !top streak - Maior killstreak
        !top coins - Mais rico em DZ Coins
        !top playtime - Mais tempo jogado
    """
    
    if not categoria:
        # Menu principal
        embed = discord.Embed(
            title="🏆 LEADERBOARD - BIGODE TEXAS",
            description="Escolha uma categoria para ver o ranking:",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="📊 Categorias Disponíveis",
            value=(
                "🔫 `!top kills` - Top Matadores\n"
                "🎯 `!top kd` - Melhor K/D Ratio\n"
                "🔥 `!top streak` - Maior Killstreak\n"
                "💰 `!top coins` - Mais Rico\n"
                "⏰ `!top playtime` - Mais Tempo Jogado"
            ),
            inline=False
        )
        
        embed.set_footer(text="BigodeTexas • Sistema de Rankings", icon_url=FOOTER_ICON)
        await ctx.send(embed=embed)
        return
    
    categoria = categoria.lower()
    
    # Carrega dados
    players_db = load_json(PLAYERS_DB_FILE)
    economy = load_json(ECONOMY_FILE)
    
    if not players_db and categoria not in ["coins"]:
        await ctx.send("❌ Ainda não há dados de jogadores suficientes para gerar rankings!")
        return
    
    # Processa ranking baseado na categoria
    if categoria == "kills":
        await show_kills_leaderboard(ctx, players_db)
    elif categoria == "kd":
        await show_kd_leaderboard(ctx, players_db)
    elif categoria == "streak":
        await show_streak_leaderboard(ctx, players_db)
    elif categoria == "coins":
        await show_coins_leaderboard(ctx, economy)
    elif categoria == "playtime":
        await show_playtime_leaderboard(ctx, players_db)
    else:
        await ctx.send(f"❌ Categoria inválida! Use `!top` para ver as opções.")

async def show_kills_leaderboard(ctx, players_db):
    """Mostra ranking de kills"""
    # Ordena por kills
    sorted_players = sorted(
        players_db.items(),
        key=lambda x: x[1].get('kills', 0),
        reverse=True
    )[:10]
    
    if not sorted_players:
        await ctx.send("❌ Nenhum dado de kills disponível ainda!")
        return
    
    embed = discord.Embed(
        title="🔫 TOP 10 MATADORES",
        description="Os pistoleiros mais letais do servidor!",
        color=discord.Color.red()
    )
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for idx, (player_name, stats) in enumerate(sorted_players):
        kills = stats.get('kills', 0)
        deaths = stats.get('deaths', 0)
        kd = calculate_kd(kills, deaths)
        level = calculate_level(kills)
        
        embed.add_field(
            name=f"{medals[idx]} {player_name}",
            value=f"💀 Kills: **{kills}** | 🎯 K/D: **{kd}** | ⭐ Nível: **{level}**",
            inline=False
        )
    
    embed.set_footer(text="BigodeTexas • Atualizado em tempo real", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)

async def show_kd_leaderboard(ctx, players_db):
    """Mostra ranking de K/D ratio"""
    # Filtra jogadores com pelo menos 5 kills (evita K/D inflado)
    qualified_players = {
        name: stats for name, stats in players_db.items()
        if stats.get('kills', 0) >= 5
    }
    
    if not qualified_players:
        await ctx.send("❌ Nenhum jogador com kills suficientes (mínimo 5) para ranking de K/D!")
        return
    
    # Ordena por K/D
    sorted_players = sorted(
        qualified_players.items(),
        key=lambda x: calculate_kd(x[1].get('kills', 0), x[1].get('deaths', 0)),
        reverse=True
    )[:10]
    
    embed = discord.Embed(
        title="🎯 TOP 10 K/D RATIO",
        description="Os jogadores mais eficientes em combate!\n*(Mínimo 5 kills)*",
        color=discord.Color.blue()
    )
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for idx, (player_name, stats) in enumerate(sorted_players):
        kills = stats.get('kills', 0)
        deaths = stats.get('deaths', 0)
        kd = calculate_kd(kills, deaths)
        
        embed.add_field(
            name=f"{medals[idx]} {player_name}",
            value=f"🎯 K/D: **{kd}** | 💀 Kills: **{kills}** | ☠️ Deaths: **{deaths}**",
            inline=False
        )
    
    embed.set_footer(text="BigodeTexas • Atualizado em tempo real", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)

async def show_streak_leaderboard(ctx, players_db):
    """Mostra ranking de killstreak"""
    # Ordena por best_killstreak
    sorted_players = sorted(
        players_db.items(),
        key=lambda x: x[1].get('best_killstreak', 0),
        reverse=True
    )[:10]
    
    if not sorted_players or sorted_players[0][1].get('best_killstreak', 0) == 0:
        await ctx.send("❌ Nenhum killstreak registrado ainda!")
        return
    
    embed = discord.Embed(
        title="🔥 TOP 10 KILLSTREAKS",
        description="As maiores sequências de kills sem morrer!",
        color=discord.Color.orange()
    )
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for idx, (player_name, stats) in enumerate(sorted_players):
        best_streak = stats.get('best_killstreak', 0)
        if best_streak == 0:
            break
            
        current_streak = stats.get('killstreak', 0)
        kills = stats.get('kills', 0)
        
        streak_status = f"🔥 **ATIVO: {current_streak}**" if current_streak > 0 else "💀 Morreu"
        
        embed.add_field(
            name=f"{medals[idx]} {player_name}",
            value=f"🏆 Melhor: **{best_streak}** kills | {streak_status} | Total: **{kills}**",
            inline=False
        )
    
    embed.set_footer(text="BigodeTexas • Atualizado em tempo real", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)

async def show_coins_leaderboard(ctx, economy):
    """Mostra ranking de DZ Coins"""
    if not economy:
        await ctx.send("❌ Nenhum jogador com DZ Coins ainda!")
        return
    
    # Ordena por balance
    sorted_players = sorted(
        economy.items(),
        key=lambda x: x[1].get('balance', 0),
        reverse=True
    )[:10]
    
    # Filtra jogadores com saldo > 0
    sorted_players = [(uid, data) for uid, data in sorted_players if data.get('balance', 0) > 0]
    
    if not sorted_players:
        await ctx.send("❌ Nenhum jogador com DZ Coins ainda!")
        return
    
    embed = discord.Embed(
        title="💰 TOP 10 MAIS RICOS",
        description="Os jogadores com mais DZ Coins!",
        color=discord.Color.gold()
    )
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for idx, (user_id, data) in enumerate(sorted_players):
        balance = data.get('balance', 0)
        gamertag = data.get('gamertag', 'Não vinculada')
        
        try:
            user = await bot.fetch_user(int(user_id))
            username = user.name
        except:
            username = f"User {user_id}"
        
        embed.add_field(
            name=f"{medals[idx]} {username}",
            value=f"💵 **{balance:,} DZ Coins** | 🎮 Gamertag: {gamertag}",
            inline=False
        )
    
    embed.set_footer(text="BigodeTexas • Sistema Econômico", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)

async def show_playtime_leaderboard(ctx, players_db):
    """Mostra ranking de tempo jogado"""
    # Ordena por total_playtime
    sorted_players = sorted(
        players_db.items(),
        key=lambda x: x[1].get('total_playtime', 0),
        reverse=True
    )[:10]
    
    if not sorted_players or sorted_players[0][1].get('total_playtime', 0) == 0:
        await ctx.send("❌ Nenhum dado de tempo jogado disponível ainda!")
        return
    
    embed = discord.Embed(
        title="⏰ TOP 10 TEMPO JOGADO",
        description="Os sobreviventes mais dedicados!",
        color=discord.Color.purple()
    )
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for idx, (player_name, stats) in enumerate(sorted_players):
        playtime = stats.get('total_playtime', 0)
        if playtime == 0:
            break
        
        hours = int(playtime // 3600)
        minutes = int((playtime % 3600) // 60)
        
        kills = stats.get('kills', 0)
        
        embed.add_field(
            name=f"{medals[idx]} {player_name}",
            value=f"⏰ **{hours}h {minutes}m** jogadas | 💀 {kills} kills",
            inline=False
        )
    
    embed.set_footer(text="BigodeTexas • Atualizado em tempo real", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)
