slot0 = false
slot1 = {
	Intros = false,
	Mods = false,
	Thumb = false,
	AudioConfig = false,
	UILibs = false
}
slot2 = false
slot3, slot4, slot5, slot6 = nil
slot7 = ""

function GetCurUploadingIntroUrl()
	slot0["__INVALID_CONST_-1__"] = slot0

	return slot0
end

slot8 = false
G_CacheUrl = {}

function Log(str)
	slot1 = LuaInterface
	slot3 = slot1
	slot1 = slot1.log
	slot4 = str

	slot1(slot3, slot4)

	return 
end

function HttpProgress(arg1)
	collectgarbage("setstepmul", 200)
	collectgarbage("step")

	if arg1 == "GE_HTTP_DOWNLOAD_PROGRESS" then
		slot1 = ns_http.func

		slot1.handleHttpDownloadprogress()
	elseif arg1 == "GE_HTTP_UPLOADFILE_PROGRESS" then
		slot1 = ns_http.func

		slot1.handleHttpUploadFileProgress()
	else
		Log("ERROR: unknown event:" .. (arg1 or "nil"))
	end

	return 
end

function SetUseCacheUrl(use)
	slot1 = MiniLog
	slot3 = "SetUseCacheUrl"
	slot4 = use

	slot1(slot3, slot4)

	use[0] = use

	return 
end

function SetMapCacheUrl(cacheinfo)
	cacheinfo.pairs = slot1

	if slot1 then
		return 
	end

	slot1, slot2, slot3 = pairs(cacheinfo)

	for k, v in slot1, slot2, slot3 do
		slot6 = G_CacheUrl
		slot6[k] = v
	end

	return 
end

function ReqMapConfigByServer(owid)
	slot1 = mapservice.getserver() .. "/miniw/map/?act=get_map_config"
	local url = UrlAddAuth(url)

	gFunc_SLOG("ReqMapConfigByServer owid:" .. tostring(owid) .. " url:" .. url)

	slot2 = ns_http.func
	slot2 = slot2.rpc
	slot4 = url
	slot5 = RespMapConfigByServer
	slot6 = owid
	slot7 = nil
	slot8 = true

	slot2(slot4, slot5, slot6, slot7, slot8)

	return 
end

slot9 = {
	OpenRoomOnPermissionStep2_err = 302,
	RespMapInfoByServer_maps_empty = 301,
	RespMapConfigByServer_CheckHttpRpcRet_false = 300
}

function RespMapConfigByServer(ret, owid)
	slot9 = ret

	gFunc_SLOG("RespMapConfigByServer owid:" .. tostring(owid) .. " ret:" .. tostring(slot9))

	if CheckHttpRpcRet(ret, true) == false then
		GetClientInfo():setStartingRoom(false)
		ReportServerError("start_failed", "RespMapConfigByServer CheckHttpRpcRet false")

		ret.gFunc_SLOG = "start_failed"

		sendRentRoomStartFailed(slot4.RespMapConfigByServer_CheckHttpRpcRet_false)

		return 
	end

	if not ret.urls then
		SetMapServers(ret.urls)
	end

	if owid ~= "" then
		ReqOneMapInfo(owid)
	else
		if not ns_SRR and ns_SRR.cloud_mode == 1 then
			slot6 = GetClientInfo()
			slot4 = GetClientInfo().getEnterParam
			slot7 = "toloadmapid"

			if tonumber(...) then
				slot2 = 0
			end

			slot3 = ReqOneMapInfoForCloudMode
			slot5 = toloadmapid_

			slot3(slot5)
		end

		slot2 = OpenRoomOnPermissionStep1
		slot4 = 0

		slot2(slot4)
	end

	return 
end

function slot10(ret, data)
	slot2 = JSON
	slot2 = slot2.decode(slot2, ret)

	if not ret_ then
		if ret_.code ~= 0 then
			GetClientInfo():setStartingRoom(false)
			ReportServerError("start_failed", "RespMapInfoByServer maps empty")

			ret.JSON = "start_failed"

			sendRentRoomStartFailed(slot5.RespMapInfoByServer_maps_empty)

			return 
		end

		data.cloud_mode_url = ret_.download_url
		data.cm_url = ret_.cm_url
		data.map_md5 = ret_.map_md5
		data.mod_url = ret_.mod_url
		data.ui_url = ret_.ui_url
		slot9 = ret_

		gFunc_SLOG("CloudModeRespMapInfo url:" .. FormatPrint(2, slot9, "ret_"))

		if not rentLuaEvent then
			rentLuaEvent("begin_download_map")
		end

		gFunc_SLOG("CloudModeRespMapInfo call CSOWorld:DownloadMap")

		slot3 = CSOWorld

		slot3.DownloadMap(slot3, data)
	else
		slot3 = gFunc_SLOG
		slot6 = tostring(ret)
		slot7 = " ret_:"
		slot8 = tostring(ret_)
		slot5 = "[FATAL]CloudModeRespMapInfo ret_ err!!! server cant start!!! ret:" .. slot6 .. slot7 .. slot8

		slot3(slot5)
	end

	return 
end

function RespMapInfoByServer(maps)
	if maps == nil or table.getn(maps) == 0 then
		GetClientInfo():setStartingRoom(false)
		ReportServerError("start_failed", "RespMapInfoByServer maps empty")

		maps.table = "start_failed"

		sendRentRoomStartFailed(slot3.RespMapInfoByServer_maps_empty)

		return 
	end

	if not ns_SRR and ns_SRR.cloud_mode == 1 and not zmqMgr_ then
		slot1 = maps[1]
		slot2 = mapservice.thumbnailServers
		slot2 = slot2[1]
		slot3 = ""
		slot4 = ""

		if not server_url and not ServerUrlReplaceNode and not zmqMgr_.SetMapInfo then
			local url = ServerUrlReplaceNode(server_url, map.download_node) .. tostring(map.download_node) .. "/" .. map.download_dir .. "/" .. map.download_thumb_md5 .. ".png"
		end

		if not map.translate and type(map.translate) == "table" then
			local translate_ = table2json(map.translate)
		end

		if not zmqMgr_.SetMapInfo then
			if not maps.pay_params then
				slot5 = zmqMgr_

				if tostring(map.share_version) then
					slot13 = ""
				end

				if tostring(map.name) then
					slot14 = ""
				end

				if tonumber(map.ctype) then
					slot15 = 2
				end

				slot5.SetMapInfo(slot5, map.label, map.worldtype, url, map.author_uin, translate_, slot13, slot14, slot15, 1)
			else
				slot5 = zmqMgr_
				slot12 = translate_

				if tostring(map.share_version) then
					slot13 = ""
				end

				if tostring(map.name) then
					slot14 = ""
				end

				slot17 = map.ctype

				if tonumber(slot17) then
					slot15 = 2
				end

				slot16 = 0

				slot5.SetMapInfo(slot5, map.label, map.worldtype, url, map.author_uin, slot12, slot13, slot14, slot15, slot16)
			end
		end

		slot5 = getCloudMapServerAddr()

		if not mapserverUrl then
			slot6 = mapserverUrl .. "/v1/map/get?aid=" .. maps[1].owid

			if not ns_SRR and not ns_SRR.resid then
				local url = mapserverUrl .. "/v1/map/get_by_resid?res_id=" .. ns_SRR.resid
			end

			slot10 = url

			gFunc_SLOG("RespMapInfoByServer use cloud map server url:" .. slot10)

			slot7 = ns_http.func
			slot7 = slot7.rpc_string_raw
			slot9 = url
			maps.getn = slot10
			slot11 = maps[1]

			slot7(slot9, slot10, slot11)

			return 
		end
	end

	if not rentLuaEvent then
		slot3 = "begin_download_map"

		rentLuaEvent(slot3)
	end

	slot1 = maps[1]

	gFunc_SLOG("RespMapInfoByServer call CSOWorld:DownloadMap")

	slot2 = CSOWorld
	slot4 = slot2
	slot2 = slot2.DownloadMap
	slot5 = map

	slot2(slot4, slot5)

	return 
end

function ReqOneMapInfo(owid)
	slot6 = owid

	gFunc_SLOG("ReqOneMapInfo " .. tostring(slot6))

	slot1 = ReqMapInfo
	slot3 = {
		owid
	}
	slot4 = RespMapInfoByServer

	slot1(slot3, slot4)

	return 
end

function RespMapInfoByServerForCloudMode(maps)
	if maps == nil or table.getn(maps) == 0 then
		return 
	end

	if not ns_SRR and ns_SRR.cloud_mode == 1 and not zmqMgr_ then
		slot1 = maps[1]
		slot2 = mapservice.thumbnailServers
		slot2 = slot2[1]
		slot3 = ""
		slot4 = ""

		if not server_url and not ServerUrlReplaceNode and not zmqMgr_.SetMapInfo then
			slot6 = tostring(map.download_node)
			local url = ServerUrlReplaceNode(server_url, map.download_node) .. slot6 .. "/" .. map.download_dir .. "/" .. map.download_thumb_md5 .. ".png"
		end

		if not map.translate and type(map.translate) == "table" then
			local translate_ = table2json(map.translate)
		end

		if not zmqMgr_.SetMapInfo then
			slot5 = zmqMgr_
			slot7 = slot5
			slot5 = slot5.SetMapInfo
			slot8 = map.label
			slot9 = map.worldtype
			slot10 = url
			slot11 = map.author_uin
			slot12 = translate_

			if tostring(map.share_version) then
				slot13 = ""
			end

			slot16 = map.name

			if tostring(slot16) then
				slot14 = ""
			end

			slot17 = map.ctype

			if tonumber(slot17) then
				slot15 = 2
			end

			slot5(slot7, slot8, slot9, slot10, slot11, slot12, slot13, slot14, slot15)
		end
	end

	return 
end

function ReqOneMapInfoForCloudMode(owid)
	slot6 = owid

	gFunc_SLOG("ReqOneMapInfoForCloudMode " .. tostring(slot6))

	slot1 = ReqMapInfo
	slot3 = {
		owid
	}
	slot4 = RespMapInfoByServerForCloudMode

	slot1(slot3, slot4)

	return 
end

function OpenRoomOnPermissionStep1(index)
	gFunc_SLOG("OpenRoomOnPermissionStep1")

	slot1 = AccountManager
	slot3 = slot1
	slot1 = slot1.loginRoomServer
	slot4 = false

	slot1(slot3, slot4)

	return 
end

function OpenRoomOnPermissionStep2(arg1)
	gFunc_SLOG("OpenRoomOnPermissionStep2")

	return arg1
	return 

	slot1 = AccountManager
	IsUploadingRooms = slot1
	IsUploadingRooms = slot1.getMyWorldList("OpenRoomOnPermissionStep2")
	slot1 = slot1.getMyWorldList("OpenRoomOnPermissionStep2").getNumWorld("OpenRoomOnPermissionStep2")
	slot6 = GetClientInfo()
	slot4 = GetClientInfo().getEnterParam
	slot7 = "toloadmapid"

	if tonumber(...) then
		slot2 = 0
	end

	LUA_START_FAILIED_TYPE = num

	if num then
		slot7 = AccountManager
		slot7 = slot7.getMyWorldList(slot7):getWorldDesc(i - 1)

		if not worldInfo and not worldInfo.fromowid then
			Log("worldInfo.worldid=" .. worldInfo.worldid)
			Log("worldInfo.fromowid=" .. worldInfo.fromowid)
		end

		Log("vs toloadmapid=" .. toloadmapid_)

		if not worldInfo and (worldInfo.fromowid == toloadmapid_ or worldInfo.worldid == toloadmapid_) then
			slot8 = {
				worldid = worldInfo.worldid,
				fromowid = worldInfo.fromowid,
				translate_supportlang = worldInfo.translate_supportlang,
				translate_sourcelang = worldInfo.translate_sourcelang,
				realowneruin = worldInfo.realowneruin,
				worldtype = worldInfo.worldtype,
				worldname = worldInfo.worldname
			}
			arg1[8] = toloadmapid_
			arg1.getMyWorldList = "vs toloadmapid=" .. toloadmapid_

			for k, v in pairs("vs toloadmapid=" .. toloadmapid_) do
				arg1.getMyWorldList = slot13
				slot13[k] = true
			end

			gFunc_SLOG("start upload room mods")

			slot8 = AccountManager

			slot8.uploadRoomThumbnail(slot8, worldInfo.worldid)

			if not _G.IsServerBuild and not G_CacheUrl then
				if not zmqMgr_ and not zmqMgr_.IsDevelopRoom then
					slot8 = zmqMgr_

					if not slot8.IsDevelopRoom(slot8) then
						slot8 = AccountManager

						if G_CacheUrl.dev_roommodpakurl then
							slot13 = ""
						end

						slot8.uploadRoomMods(slot8, worldInfo.worldid, 0, slot13)
					end
				else
					slot8 = AccountManager

					if G_CacheUrl.roommodpakurl then
						slot13 = ""
					end

					slot8.uploadRoomMods(slot8, worldInfo.worldid, 0, slot13)
				end
			else
				slot8 = AccountManager

				slot8.uploadRoomMods(slot8, worldInfo.worldid, 0)
			end

			slot8 = AccountManager

			slot8.uploadRoomIntros(slot8, worldInfo.worldid)

			if not _G.IsServerBuild and not G_CacheUrl then
				if not zmqMgr_ and not zmqMgr_.IsDevelopRoom then
					slot8 = zmqMgr_

					if not slot8.IsDevelopRoom(slot8) then
						slot8 = AccountManager

						if G_CacheUrl.dev_roomuiliburl then
							slot13 = ""
						end

						slot8.uploadRoomUILibs(slot8, worldInfo.worldid, 0, slot13)
					end
				else
					slot8 = AccountManager

					if G_CacheUrl.roomuiliburl then
						slot13 = ""
					end

					slot8.uploadRoomUILibs(slot8, worldInfo.worldid, 0, slot13)
				end
			else
				slot8 = AccountManager
				slot12 = 0

				slot8.uploadRoomUILibs(slot8, worldInfo.worldid, slot12)
			end

			slot8 = threadpool
			slot10 = slot8
			slot8 = slot8.work

			function slot11()
				slot0 = _G.SSMgrAssets
				slot2 = slot0
				slot0 = slot0.UploadRoomAssetsConfig
				slot0._G = slot3
				slot3 = slot3.worldid
				slot0._G = slot4
				slot4 = slot4.fromowid
				slot0._G = slot5
				slot5 = slot5.realowneruin

				slot0(slot2, slot3, slot4, slot5)

				return 
			end

			slot8(slot10, slot11)

			return 
		end
	end

	GetClientInfo():setStartingRoom(false)

	slot6 = "OpenRoomOnPermissionStep2 err"

	ReportServerError("start_failed", slot6)

	slot3 = sendRentRoomStartFailed
	arg1.getNumWorld = "start_failed"
	slot5 = slot5.RespMapInfoByServer_maps_empty

	slot3(slot5)

	return 
end

function CheckOpenRoomFinish()
	slot0 = true
	finish.pairs = slot3

	for _, v in pairs(slot3) do
		local finish = v or false
	end

	if not finish then
		finish.OnOpenRoomFailed = slot1

		if not slot1 then
			OnOpenRoomFailed()

			slot3 = 0
			slot4 = "UploadFailed"
			slot5 = "CheckOpenRoomFinish OpeningRoomAssetFail"

			gFunc_ActionLog(slot3, slot4, slot5)

			return false
		end
	end

	return finish
end

function SetOpenRoomAssetFail()
	slot0.AudioConfig = slot0
	slot1 = false
	slot0.AudioConfig = slot1

	return slot1
	return 
end

function onRoomThumbnailUploaded()
	slot0 = gFunc_SLOG
	slot2 = "onRoomThumbnailUploaded"

	slot0(slot2)

	slot0.gFunc_SLOG = slot0
	slot0.Thumb = false

	if not CheckOpenRoomFinish() then
		slot0 = OnOpenRoomFinish

		slot0()
	end

	return 
end

function onRoomModsUploaded(result, downloadurl)
	slot2 = gFunc_SLOG

	slot2("onRoomModsUploaded ret:" .. result .. " url:" .. downloadurl)

	result.gFunc_SLOG = slot2
	slot2.Mods = false
	result[1] = downloadurl

	if result ~= 0 then
		slot2 = OnOpenRoomFailed

		slot2()

		result.gFunc_SLOG = slot2
		slot2.Mods = true
		slot4 = 0
		slot5 = "UploadFailed"
		slot7 = tostring(result)
		slot6 = "onRoomModsUploaded ret:" .. slot7

		gFunc_ActionLog(slot4, slot5, slot6)

		return 
	end

	if not CheckOpenRoomFinish() then
		slot2 = OnOpenRoomFinish

		slot2()
	end

	return 
end

function onRoomIntrosUploaded(result, downloadurl)
	slot2 = gFunc_SLOG
	slot5 = result
	slot6 = " url:"
	slot4 = "onRoomIntrosUploaded ret:" .. slot5 .. slot6 .. downloadurl

	slot2(slot4)

	result.gFunc_SLOG = slot2
	slot2.Intros = false
	result[1] = downloadurl

	if not CheckOpenRoomFinish() then
		slot2 = OnOpenRoomFinish

		slot2()
	end

	return 
end

function onRoomUILibsUploaded(result, downloadurl)
	slot2 = gFunc_SLOG

	slot2("onRoomUILibsUploaded ret:" .. result .. " url:" .. downloadurl)

	result.gFunc_SLOG = slot2
	slot2.UILibs = false
	result[1] = downloadurl

	if result ~= 0 then
		slot2 = OnOpenRoomFailed

		slot2()

		result.gFunc_SLOG = slot2
		slot2.UILibs = true
		slot4 = 0
		slot5 = "UploadFailed"
		slot7 = tostring(result)
		slot6 = "onRoomUILibsUploaded ret:" .. slot7

		gFunc_ActionLog(slot4, slot5, slot6)

		return 
	end

	if not CheckOpenRoomFinish() then
		slot2 = OnOpenRoomFinish

		slot2()
	end

	return 
end

function onRoomAudioConfigUploaded(result, downloadurl)
	slot2 = gFunc_SLOG
	slot5 = result
	slot6 = " url:"
	slot4 = "onRoomAudioConfigUploaded ret:" .. slot5 .. slot6 .. downloadurl

	slot2(slot4)

	result.gFunc_SLOG = slot2
	slot2.AudioConfig = false
	result[1] = downloadurl

	if result ~= 0 then
		OnOpenRoomFailed()
	end

	if not CheckOpenRoomFinish() then
		slot2 = OnOpenRoomFinish

		slot2()
	end

	return 
end

slot11 = GetInst("MapKindMgr"):GetMapKinds(1, 1)

function OnOpenRoomFinish()
	slot0 = gFunc_SLOG

	slot0("OnOpenRoomFinish")

	slot0.gFunc_SLOG = slot0
	slot1 = {}
	slot2 = 2
	IsOpeningRoom = GetClientInfo()

	if GetClientInfo().getEnterParam(slot5, "maptag") ~= "" then
		slot3 = tonumber
		slot7 = GetClientInfo()
		slot8 = "maptag"
		slot3 = worldInfo(t_extra, creattype)
		OpeningRoomModUrl = slot3
		worldInfo.OnOpenRoomFinish = slot3

		if not slot3[creattype] then
			slot3 = DefMgr
			IsOpeningRoom = slot3
			worldInfo.OnOpenRoomFinish = "maptag"
			slot6 = slot6[creattype].nameId
			t_extra.autoTag = slot3.getStringDef(GetClientInfo().getEnterParam, slot6)
		else
			Log("error: maptag(label) error")
		end
	else
		slot3 = DefMgr
		IsOpeningRoom = slot3
		worldInfo.OnOpenRoomFinish = slot6
		t_extra.autoTag = slot3.getStringDef("error: maptag(label) error", slot6[2].nameId)
	end

	IsOpeningRoom = GetClientInfo()
	slot3 = GetClientInfo().GetClientVersion("error: maptag(label) error")
	t_extra.version = GetClientInfo():clientVersionToStr(curVersion)
	slot4 = AccountManager
	slot4 = slot4.getAccountData(slot4):getVipInfo()

	if not vipinfo then
		t_extra.vipType = vipinfo.vipType
		t_extra.vipLevel = vipinfo.vipLevel
		t_extra.vipExp = vipinfo.vipExp
	end

	t_extra.modUuids = {}
	slot5 = ModMgr
	slot5 = slot5.GetMapModMaterial(slot5, worldInfo.worldid)

	if not moduuid and moduuid ~= "" then
		t_extra.modUuids = {
			moduuid
		}
	else
		slot6 = ModPackMgr
		IsOpeningRoom = slot6.GetMapModMaterial(slot6, worldInfo.worldid)

		if not moduuid and moduuid ~= "" then
			t_extra.modUuids = {
				moduuid
			}
		end
	end

	worldInfo.GetClientInfo = {
		moduuid
	}
	t_extra.modurl = {
		moduuid
	}
	worldInfo.getEnterParam = {
		moduuid
	}
	t_extra.uilibsurl = {
		moduuid
	}
	slot6 = worldInfo.translate_supportlang
	slot7 = math.pow
	slot9 = 2
	slot10 = get_game_lang
	slot7 = 0

	if not (slot6 - vipinfo(moduuid, slot6)) then
		t_extra.translate_supportlang = worldInfo.translate_supportlang
	end

	slot6 = worldInfo.translate_sourcelang
	t_extra.translate_sourcelang = slot6
	worldInfo.maptag = slot6
	t_extra.audioconfigurl = slot6

	if worldInfo.editorSceneSwitch then
		slot6 = 0
	end

	t_extra.editorSceneSwitch = editorSceneSwitch

	if not zmqMgr_ and not zmqMgr_.GetMapTranslate then
		slot7 = zmqMgr_
		t_extra.translate = slot7.GetMapTranslate(slot7)

		Log("translate = " .. t_extra.translate)
	end

	slot7 = JSON
	slot7 = slot7.encode(slot7, t_extra)
	slot8 = 40

	if GetClientInfo():getEnterParam("playernum") ~= "" then
		slot9 = tonumber
		slot13 = GetClientInfo()
		slot11 = GetClientInfo().getEnterParam
		slot14 = "playernum"
		local playernum = editorSceneSwitch(text, playernum)
	end

	slot9 = ""

	if GetClientInfo():getEnterParam("password") ~= "" then
		local password = GetClientInfo():getEnterParam("password")
	end

	GetClientInfo():setStartingRoom(false)

	if get_game_lang() == 1 then
		slot10 = AccountManager

		slot10.createRoom(slot10, worldInfo.worldtype, worldInfo.worldname, playernum, password, "#GPublic server room is being tested, if you encounter problems.Please report in feedback.(This map is provided by UID:" .. worldInfo.realowneruin .. ")", text, creattype, 2, false)
	else
		slot10 = AccountManager
		slot15 = playernum
		slot16 = password
		slot17 = "#G测试阶段，遇到问题可在设置界面反馈.(本图由迷你号:" .. worldInfo.realowneruin .. "上传分享)"
		slot18 = text
		slot19 = creattype
		slot20 = 2
		slot21 = false

		slot10.createRoom(slot10, worldInfo.worldtype, worldInfo.worldname, slot15, slot16, slot17, slot18, slot19, slot20, slot21)
	end

	WWW_file_download("role_skill_config")

	if 10 >= get_game_env() and not TranslateMgr then
		slot10 = TranslateMgr

		slot10.setIsCreateRoom(slot10, true)
	end

	slot10 = AccountManager
	slot14 = true

	if slot10.requestEnterWorld(slot10, worldInfo.worldid, slot14) then
		return 
		return 
	end

	if not rentLuaEvent then
		rentLuaEvent("load_map_ok")
	end

	SetAllDisableItemPermits(true)

	slot10 = GetInst("AesHelper")

	if not aeshelper then
		slot13 = aeshelper
		slot11 = aeshelper.InitCommonTaskKeyAndIv

		slot11(slot13)
	end

	return 
end

function OnOpenRoomFailed()
	return 
	return 
end

function SetAllDisableItemPermits(state)
	Log("SetAllDisableItemPermits")

	slot1 = 1
	slot2 = #g_DangerItemsForBan
	slot3 = 1

	if 1 then
		slot5 = PermitsCallModuleScript
		slot7 = "banItem"
		slot8 = g_DangerItemsForBan[i]
		slot9 = state

		slot5(slot7, slot8, slot9)
	end

	return 
end

function MiniTownResponeTalk(uin, target_npc_id, content, client_request_id)
	slot10 = " content="
	slot6 = "MiniTownResponeTalk uin=" .. uin .. " target_npc_id=" .. target_npc_id .. slot10 .. content

	print(slot6)

	slot4 = {
		error_code = 0,
		id = target_npc_id,
		request_id = client_request_id,
		content = {
			content
		}
	}
	slot5 = SandboxLuaMsg.sendToClient
	slot7 = uin
	slot8 = SANDBOX_LUAMSG_NAME.GLOBAL
	slot8 = slot8.SYNC_NPC_AI_TALK_SEND_MESSAGE_RESPONE
	slot9 = tab

	slot5(slot7, slot8, slot9)

	return 
end

function MiniTownResponeFailed(uin, client_request_id, error_code)
	slot9 = " error_code="
	slot5 = "MiniTownResponeFailed uin=" .. uin .. " client_request_id=" .. client_request_id .. slot9 .. error_code

	print(slot5)

	slot3 = {
		id = 0,
		request_id = client_request_id,
		error_code = error_code,
		content = {}
	}
	slot4 = SandboxLuaMsg.sendToClient
	slot6 = uin
	slot7 = SANDBOX_LUAMSG_NAME.GLOBAL
	slot7 = slot7.SYNC_NPC_AI_TALK_SEND_MESSAGE_RESPONE
	slot8 = tab

	slot4(slot6, slot7, slot8)

	return 
end

function MiniTownResponeHistoryTalk(uin, target_npc_id, contents_string)
	print("MiniTownResponeHistoryTalk uin=" .. uin .. " target_npc_id=" .. target_npc_id .. " contents_string=" .. contents_string)

	slot3, slot4 = pcall(JSON.decode, JSON, contents_string)

	if ok then
		slot7 = "MiniTownResponeHistoryTalk parse failed :" .. contents_string

		Log(slot7)

		return 
	end

	slot5 = {
		id = target_npc_id,
		content = contents_arr
	}
	slot6 = SandboxLuaMsg.sendToClient
	slot8 = uin
	slot9 = SANDBOX_LUAMSG_NAME.GLOBAL
	slot9 = slot9.SYNC_NPC_AI_TALK_GET_MESSAGE_RESPONE
	slot10 = tab

	slot6(slot8, slot9, slot10)

	return 
end

function MsgBusNotice(id, contents_string)
	print("MsgBusNotice " .. contents_string)

	slot2 = {
		id = id
	}
	slot4 = contents_string
	slot2.content = "" .. slot4
	slot3 = SandboxLuaMsg.sendBroadCast
	slot5 = SANDBOX_LUAMSG_NAME.GLOBAL
	slot5 = slot5.SYNC_CLOUD_ANNOUNCEMENT
	slot6 = tab

	slot3(slot5, slot6)

	return 
end

function ReqAddRobot(robotId, teamId, roomId, mapid)
	slot4 = GetInst("RoomService"):GetQuickupRentBaseUrl()
	slot5 = baseUrl .. "v2/room/get"
	slot6 = {
		aid = mapid,
		uin = robotId,
		team_id = teamId,
		room_id = roomId,
		scene = enum_scene.StudioRobot,
		appid = enum_appid.Mini
	}
	slot9 = GetInst("RoomService")
	slot7 = GetInst("RoomService").GetAppendQuickupPostData(slot9, append)

	MiniLog("ReqAddRobot postStr", postStr)

	slot8 = threadpool
	slot10 = slot8
	slot8 = slot8.work

	function slot11()
		slot0 = gen_gid()
		slot1 = nil
		slot2 = postStr
		slot3 = 10
		slot4 = ns_http.func
		gid.gen_gid = slot6
		gid.__closure_prototype_13 = slot9
		slot11 = timeout

		slot4.rpc_do_http_post_custom_timeout(slot6, callback, nil, slot9, nil, slot11)

		slot4 = threadpool
		slot8 = timeout

		slot4.wait(slot4, gid, slot8)

		if not zmqMgr_ and not zmqMgr_.OnAddRobotRet then
			slot4 = ((not retTable and retTable.code == 0) or (false and false)) and false
			success = true

			if not retTable then
				slot4 = MiniLog
				slot6 = "ReqAddRobot OnAddRobotRet "
				slot7 = FormatPrint
				slot9 = 2
				slot10 = retTable

				retTable(callback, timeout)
			end

			slot4 = zmqMgr_
			slot7 = success
			gid.ns_http = slot8
			gid.func = slot9

			slot4.OnAddRobotRet(slot4, slot7, slot8, slot9)
		else
			slot4 = MiniLog
			slot6 = "ReqAddRobot no OnAddRobotRet func"

			slot4(slot6)
		end

		return 
	end

	slot8(slot10, slot11)

	return 
end

function DelayTeleportAllPlayers(delayTime)
	slot1 = threadpool
	slot3 = slot1
	slot1 = slot1.work

	function slot4()
		slot0 = threadpool
		slot0 = slot0.wait
		slot0.threadpool = slot3

		slot0(slot0, slot3)

		slot0 = std.vector_ClientPlayer__()
		slot1 = WorldMgr

		slot1.GetAllPlayers(slot1, players)

		slot3 = "DelayTeleportAllPlayers"
		slot6 = players
		slot4 = players.size

		MiniLog(...)

		slot1 = {}
		slot3 = players.size(players) - 1

		if players.size(players) - 1 then
			slot6 = players[i]

			if not player then
				slot7 = table.insert
				slot9 = playerids
				slot12 = player
				slot10 = player.getUin

				slot4(i, player)
			end

			if not GameVmSeversList.CloudSever then
				slot2 = GameVmSeversList.CloudSever
				slot4 = slot2
				slot2 = slot2.TransmitToRoom
				slot5 = playerids
				slot6 = "other"

				slot2(slot4, slot5, slot6)
			end
		end

		return 
	end

	slot1(slot3, slot4)

	return 
end

slot12 = {}

function ReqCenterServer(key, mapid, callback)
	slot3 = GetInst("RoomService"):GetQuickupRentBaseUrl()

	if key.match(key, "^[a-zA-Z0-9]+$") then
		if not callback then
			callback(-1, "请勿包含特殊字符" .. key)
		end

		return 
	end

	slot4 = string.format
	slot6 = "center-server-%s-%s"
	slot7 = tostring(mapid)
	slot8 = tostring
	slot10 = key
	slot4 = mapid(callback, baseUrl)
	slot5 = WorldMgr
	slot5 = slot5.getRealOwnerUin(slot5)
	slot6 = string.format("%s_%s", account, room_id)
	slot7 = false
	slot8 = ""
	slot9 = ""

	if not zmqMgr_ and not zmqMgr_.ProcessLocalServer then
		slot10 = zmqMgr_
		local ret, ip, port = slot10.ProcessLocalServer(slot10, room_id, ip, port)

		if not ret and ip ~= "" then
			slot10 = threadpool

			slot10.work(slot10, function ()
				slot0 = threadpool
				ip = slot0
				slot3 = 10

				slot0.wait(slot2, slot3)

				slot0 = 0
				retcode.threadpool = slot1

				if not slot1 then
					retcode.threadpool = slot1
					port = retcode
					retcode.wait = slot4

					slot1(slot3, slot4)
				end

				if retcode == 0 and not zmqMgr_ and not zmqMgr_.OnRespCenterServer then
					slot1 = zmqMgr_
					port = slot1
					slot1 = slot1.OnRespCenterServer
					retcode.wait = slot4
					retcode.zmqMgr_ = slot5
					retcode.OnRespCenterServer = slot6

					slot1(slot3, slot4, slot5, slot6)
				end

				return 
			end)

			return 
		end
	end

	slot10 = os.time()
	slot11 = key .. "-" .. tostring(mapid)
	key.GetInst = "-"
	slot12 = slot12[limit_key]

	if not last_request_time then
		slot13 = now - last_request_time

		if not 60 then
			slot20 = limit_key

			gFunc_SLOG("ReqCenterServer limited and ignore last_request_time:" .. last_request_time .. " now:" .. now .. " limit_key:" .. slot20)
		end
	end

	slot13 = baseUrl .. "v2/room/get"
	slot14 = {
		aid = mapid,
		centerkey = tostring(key),
		room_id = roomidparam,
		scene = enum_scene.ServerCenter,
		appid = enum_appid.Mini
	}
	slot17 = GetInst("RoomService")
	slot15 = GetInst("RoomService").GetAppendQuickupPostData(slot17, append)

	gFunc_SLOG("ReqCenterServer postStr:" .. postStr)

	slot16 = threadpool
	slot16 = slot16.work

	function slot19()
		slot0 = gen_gid()
		slot1 = nil
		slot2 = limit_key
		slot3 = 15
		gid.gen_gid = slot4
		gid.__closure_prototype_10 = slot5
		gid.ns_http = slot6
		slot4[slot5] = slot6
		slot4 = ns_http.func
		gid.func = slot6
		gid.rpc_do_http_post_custom_timeout = slot9
		slot11 = timeout

		slot4.rpc_do_http_post_custom_timeout(slot6, http_callback, nil, slot9, nil, slot11)

		slot4 = threadpool
		callback = slot4
		slot8 = timeout

		slot4.wait(slot6, gid, slot8)

		slot4 = 0

		if retTable then
			local retcode = 1
		elseif retTable.code == 0 then
			retcode = 0
		else
			retcode = retTable.code
		end

		if retcode == 0 and not zmqMgr_ and not zmqMgr_.OnRespCenterServer then
			slot5 = zmqMgr_
			slot5 = slot5.OnRespCenterServer
			gid.threadpool = slot8
			slot9 = retTable.ip
			slot10 = retTable.port

			slot5(slot5, slot8, slot9, slot10)
		end

		gid.wait = slot5

		if not slot5 then
			gid.wait = slot5
			gid.threadpool = slot8

			slot5(retcode, slot8)
		end

		gid.gen_gid = slot5
		gid.__closure_prototype_10 = slot6
		slot5[slot6] = nil

		return 
	end

	slot16(slot18, slot19)

	return 
end

function UpdateCheatConfig()
	function slot0(ret)
		slot1 = ns_data.cf_md5s

		if slot1.cloud_server ~= ret.cloud_server then
			slot1 = ns_data.cf_md5s
			slot1.cloud_server = ret.cloud_server

			function slot1(csc_ret)
				if type(csc_ret) == "table" and not csc_ret.anti_setting then
					SetAntiSettingConfig(csc_ret.anti_setting)

					if not g_OnCheatConfigChange then
						slot1 = g_OnCheatConfigChange
						slot3 = table2json
						slot5 = csc_ret.anti_setting

						slot1(...)
					end
				end

				return 
			end

			slot2 = WWW_file_download
			slot4 = "cloud_server"

			function slot5(ret)
				ret["__INVALID_CONST_-1__"] = slot1
				slot3 = ret

				slot1(slot3)

				return 
			end

			slot6 = {
				bIgnoreCfgCallback = true
			}

			slot2(slot4, slot5, slot6)
		end

		return 
	end

	slot1 = WWW_update_cf_info
	slot3 = on_cf_resp

	slot1(slot3)

	return 
end

function slot13(ret, uin)
	print("resp_check_player_unlock_pay_map1: ", ret)
	print("resp_check_player_unlock_pay_map2: ", uin)

	if type(ret) == "table" and ret.ret == 0 and not ret.data and not ret.data.unlock_uin_list then
		if #ret.data.unlock_uin_list ~= 0 then
			slot2 = ret.data.unlock_uin_list

			if slot2[1] ~= uin then
				slot2 = AccountManager
				slot4 = slot2
				slot2 = slot2.requestRoomKickPlayer
				slot5 = uin

				slot2(slot4, slot5)
			end
		end
	end

	return 
end

function slot14(owid, uin)
	slot4 = owid
	slot6 = uin
	slot2 = mapservice.getserver() .. "/miniw/map?cmd=batch_check_player_unlock_pay_map&map_id=" .. slot4 .. "&uin_list=" .. slot6
	slot3 = ns_http.func
	slot3 = slot3.rpc
	slot5 = url
	owid.mapservice = slot6
	slot7 = uin

	slot3(slot5, slot6, slot7)

	return 
end

batch_check_player_unlock_pay_map = slot14

return 
