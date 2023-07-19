APP_VERSION = "0.2.2"
UI_VERSION = "0.9.0"

SRGF_GACHATYPE = {"2": "2", "1": "1", "11": "11", "12": "12"}
SRGF_VERSION = "v1.0"
SRGF_DATA_MODEL = {"info": {"uid": "", "lang": "zh-cn"}, "list": []}
GACHATYPE = {"始发跃迁": "2", "群星跃迁": "1", "角色活动跃迁": "11", "光锥活动跃迁": "12"}

SOFTWARE_ANNOUNCEMENT_URL = "https://raw.staticdn.net/AuroraZiling/asta.Metadata/main/announcement.txt"

CHARACTER_URL = "https://api-static.mihoyo.com/common/blackboard/sr_wiki/v1/home/content/list?app_sn=sr_wiki&channel_id=18"
PERMANENT_CHARACTER_URL = "https://raw.staticdn.net/AuroraZiling/asta.Metadata/main/metadata.json"
WEAPON_URL = "https://api-static.mihoyo.com/common/blackboard/sr_wiki/v1/home/content/list?app_sn=sr_wiki&channel_id=19"
SRGF_ITEM_ID_URL = "https://api.uigf.org/dict/starrail/{lang}.json"
SRGF_MD5_URL = "https://api.uigf.org/dict/starrail/md5.json"

COLOR_MAPPING = {"3": "#1E90FF", "4": "#7B68EE", "5": "#FFA500", "X": "#FF0000"}

FONT_MAPPING = ["StarRailNeue-Sans-Regular.otf", "StarRailNeue-Serif-Regular.otf"]
FONT_NAME_MAPPING = ["Star Rail Neue Sans-", "Star Rail Neue Serif-"]

ANNOUNCE_CURRENT_UP_URL = "https://api-takumi.mihoyo.com/common/blackboard/sr_wiki/v1/gacha_pool?app_sn=sr_wiki"

ANNOUNCE_REQUEST_URL = "https://hkrpg-api-static.mihoyo.com/common/hkrpg_cn/announcement/api/getAnnContent?game=hkrpg&game_biz=hkrpg_cn&lang=zh-cn&bundle_id=hkrpg_cn&platform=pc&region=prod_gf_cn&level=70&channel_id=1"
ANNOUNCE_ICON_REQUEST_URL = "https://hkrpg-api.mihoyo.com/common/hkrpg_cn/announcement/api/getAnnList?game=hkrpg&game_biz=hkrpg_cn&lang=zh-cn&auth_appid=announcement&authkey_ver=1&bundle_id=hkrpg_cn&channel_id=1&level=47&platform=pc&region=prod_gf_cn&sdk_presentation_style=fullscreen&sdk_screen_transparent=true&sign_type=2&uid=1"
HTML_MODEL = '''
<!DOCTYPE html>
<html>
  <head>
  <style>
    body::-webkit-scrollbar {display: none;}
    {css}
  </style>
  </head>
  <body style="background-color: transparent;">
    <article class="markdown-body" style="background-color: transparent;">
        {content}
    </article>
  </body>
</html>
'''

GITHUB_RELEASE_URL = "https://api.github.com/repos/AuroraZiling/star-rail-asta/releases/latest"

UPDATE_SCRIPT_MODEL = """
echo "DON'T CLOSE THIS WINDOW"
powershell -command \"Start-Sleep -s 3\"
powershell -command \"Get-childitem -Path .. -exclude *.json,*.zip,*.bat,temp,data -Recurse | Remove-Item -Force -Recurse\"
powershell -command \"Expand-Archive -Path .\\{filename} -DestinationPath ..\\ -Force\"
powershell -command \"Remove-Item -Path .\\{filename}\"
cd ../.
start .\\"Asta.exe\"
powershell -command \"Remove-Item -Path .\\temp\\update.bat\"
exit
"""

SRGF_JSON_SCHEMA = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "info": {
      "type": "object",
      "properties": {
        "uid": {
          "type": "string"
        },
        "lang": {
          "type": "string",
          "description": "语言 languagecode2-country/regioncode2"
        },
        "region_time_zone": {
          "type": "number",
          "description": "时区"
        },
        "export_timestamp": {
          "type": "number",
          "description": "导出 UNIX 时间戳"
        },
        "export_app": {
          "type": "string",
          "description": "导出的 App 名称"
        },
        "export_app_version": {
          "type": "string",
          "description": "导出此份记录的 App 版本号"
        },
        "srgf_version": {
          "type": "string",
          "description": "所应用的 SRGF 的版本,包含此字段以防 SRGF 出现中断性变更时，App 无法处理"
        }
      },
      "description": "包含导出方定义的基本信息",
      "required": [
        "srgf_version",
        "uid",
        "lang",
        "region_time_zone"
      ]
    },
    "list": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "gacha_id": {
            "type": "string",
            "description": "卡池 Id"
          },
          "gacha_type": {
            "type": "string",
            "description": "卡池类型",
            "enum": [
              "1",
              "2",
              "11",
              "12"
            ]
          },
          "item_id": {
            "type": "string",
            "description": "物品 Id"
          },
          "count": {
            "type": "string",
            "description": "数量，通常为1"
          },
          "time": {
            "type": "string",
            "description": "获取物品的时间"
          },
          "name": {
            "type": "string",
            "description": "物品名称"
          },
          "item_type": {
            "type": "string",
            "description": "物品类型"
          },
          "rank_type": {
            "type": "string",
            "description": "物品星级"
          },
          "id": {
            "type": "string",
            "description": "内部 Id"
          }
        },
        "required": [
          "gacha_id",
          "gacha_type",
          "item_id",
          "time",
          "id"
        ]
      },
      "description": "包含卡池记录"
    }
  },
  "required": [
    "info",
    "list"
  ]
}
