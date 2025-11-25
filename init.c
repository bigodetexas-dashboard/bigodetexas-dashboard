void main()
{
	//INIT WEATHER BEFORE ECONOMY INIT------------------------
	Weather weather = g_Game.GetWeather();

	weather.MissionWeather(false);    // false = use weather controller from Weather.c

	weather.GetOvercast().Set( Math.RandomFloatInclusive(0.4, 0.6), 1, 0);
	weather.GetRain().Set( 0, 0, 1);
	weather.GetFog().Set( Math.RandomFloatInclusive(0.05, 0.1), 1, 0);

	//INIT ECONOMY--------------------------------------
	Hive ce = CreateHive();
	if ( ce )
		ce.InitOffline();

	//DATE RESET AFTER ECONOMY INIT-------------------------
	int year, month, day, hour, minute;
	int reset_month = 9, reset_day = 20;
	GetGame().GetWorld().GetDate(year, month, day, hour, minute);

	if ((month == reset_month) && (day < reset_day))
	{
		GetGame().GetWorld().SetDate(year, reset_month, reset_day, hour, minute);
	}
	else
	{
		if ((month == reset_month + 1) && (day > reset_day))
		{
			GetGame().GetWorld().SetDate(year, reset_month, reset_day, hour, minute);
		}
		else
		{
			if ((month < reset_month) || (month > reset_month + 1))
			{
				GetGame().GetWorld().SetDate(year, reset_month, reset_day, hour, minute);
			}
		}
	}
}

// --- ESTRUTURA DE DADOS PARA O SPAWN ---
class SpawnItem
{
    string name;
    string coords; // Formato "X Y Z" ou "X Z"
}

class SpawnData
{
    ref array<ref SpawnItem> items;
    
    void SpawnData()
    {
        items = new array<ref SpawnItem>;
    }
}
// ---------------------------------------

class CustomMission: MissionServer
{
	override void OnInit()
	{
		super.OnInit();
        
        // Inicia o loop de verificação de entregas a cada 60 segundos
        GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).CallLater(CheckSpawns, 60000, true);
        Print("[BigodeBot] Sistema de Entregas Iniciado.");
	}

    void CheckSpawns()
    {
        // Caminho do arquivo que o BOT vai enviar via FTP
        // Nota: O bot deve enviar para a pasta que corresponde ao $profile (ex: SC ou config)
        string filepath = "$profile:spawns.json";
        
        if (FileExist(filepath))
        {
            Print("[BigodeBot] Arquivo de spawns encontrado. Processando...");
            
            SpawnData data = new SpawnData;
            string error;
            
            if (JsonFileLoader<SpawnData>.LoadFile(filepath, data, error))
            {
                if (data && data.items)
                {
                    foreach (SpawnItem item : data.items)
                    {
                        if (!item) continue;
                        
                        vector pos = item.coords.ToVector();
                        // Se o usuario mandou so X Z (2D), ajusta Y (altura)
                        if (pos[1] == 0)
                        {
                            pos[1] = GetGame().SurfaceY(pos[0], pos[2]);
                        }
                        
                        EntityAI obj = EntityAI.Cast(GetGame().CreateObject(item.name, pos));
                        if (obj)
                        {
                            Print("[BigodeBot] Item entregue: " + item.name + " em " + item.coords);
                        }
                        else
                        {
                            Print("[BigodeBot] FALHA ao entregar: " + item.name);
                        }
                    }
                }
                
                // Limpa o arquivo para não spawnar de novo
                // Opção 1: Deletar (DeleteFile(filepath))
                // Opção 2: Limpar conteúdo
                DeleteFile(filepath);
                Print("[BigodeBot] Entregas concluidas e arquivo limpo.");
            }
            else
            {
                Print("[BigodeBot] Erro ao ler JSON: " + error);
            }
        }
    }
}
