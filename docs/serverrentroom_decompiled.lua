ns_SRR = {
	member_list_last_sync_time = 0,
	member_list_last_sync = "",
	member_list = "",
	player_count = 0,
	owindex = 0,
	label = 0,
	playernum = 0,
	wid = 0,
	port = 0,
	ip = "",
	password = 0,
	room_id = 0,
	uin = 0,
	auth_key = "",
	last_tick = 0,
	room_run_stat = 0,
	member_team_clean_tag = "",
	rent_config = {},
	RENT_ROOM_STAT = {
		NODE_CALL_CLOSING = 21,
		NODE_LOAD_MAP = 14,
		NODE_DOWNLOAD_MAP = 13,
		NODE_ROOM_STARTING = 12,
		NODE_CALL_STARTING = 11,
		SERVER_CLOSE = 2,
		SERVER_RUNNING = 1,
		INIT = 0
	},
	member_team_desc = {}
}

function RentPrint(...)
	slot0 = LuaInterface
	slot2 = slot0
	slot0 = slot0.log

	slot0(...)

	return 
end

function RentRoomInit()
	gFunc_SLOG("call RentRoomInit")

	function do_()
		slot0 = GetClientInfo():getEnterParam("rent_config")
		slot6 = GetClientInfo()
		slot4 = GetClientInfo().getEnterParam
		slot7 = "account"

		if tonumber(...) then
			slot2 = 0
		end

		ns_SRR.uin = slot2

		if GetClientInfo():getEnterParam("room_id") then
			slot2 = 0
		end

		ns_SRR.room_id = slot2
		ns_SRR.password = GetClientInfo():getEnterParam("password")
		ns_SRR.ip = GetClientInfo():getEnterParam("ip")
		slot6 = GetClientInfo()
		slot4 = GetClientInfo().getEnterParam
		slot7 = "port"

		if tonumber(...) then
			slot2 = 0
		end

		ns_SRR.port = slot2
		slot6 = GetClientInfo()
		slot4 = GetClientInfo().getEnterParam
		slot7 = "toloadmapid"

		if tonumber(...) then
			slot2 = 0
		end

		ns_SRR.wid = slot2
		slot6 = GetClientInfo()
		slot4 = GetClientInfo().getEnterParam
		slot7 = "playernum"

		if tonumber(...) then
			slot2 = 0
		end

		ns_SRR.playernum = slot2
		slot6 = GetClientInfo()
		slot4 = GetClientInfo().getEnterParam
		slot7 = "maptag"

		if tonumber(...) then
			slot2 = 0
		end

		ns_SRR.label = slot2
		slot6 = GetClientInfo()
		slot4 = GetClientInfo().getEnterParam
		slot7 = "owindex"

		if tonumber(...) then
			slot2 = 0
		end

		ns_SRR.owindex = slot2
		slot6 = GetClientInfo()
		slot4 = GetClientInfo().getEnterParam
		slot7 = "cloud_mode"
		ns_SRR.cloud_mode = tonumber(...)
		slot6 = GetClientInfo()
		slot4 = GetClientInfo().getEnterParam
		slot7 = "rentserver_ver"

		if tonumber(...) then
			slot2 = nil
		end

		ns_SRR.rentserver_ver = slot2

		if not ns_SRR.rentserver_ver then
			if GetClientInfo():getEnterParam("rentserver_resid") then
				slot2 = nil
			end

			ns_SRR.resid = slot2
		end

		if not rent_config_file_ and 0 >= #rent_config_file_ then
			Log("rent_config_file=" .. rent_config_file_ .. ".lua")

			slot1 = io.open("devices/" .. rent_config_file_ .. ".lua", "r")

			if not ff then
				slot2 = ff.read(ff, "*a")

				ff.close(ff)

				slot3 = table_loadstring(s_)

				var_dump(t_)

				if not t_ and not t_.url then
					ns_SRR.rent_room_url = t_.url
					ns_SRR.auth_key = t_.auth_key
					ns_version.proxy_url = t_.proxy_url
					slot6 = GetClientInfo()
					slot4 = GetClientInfo().clientVersionToStr
					slot9 = GetClientInfo()
					slot7 = GetClientInfo().GetClientVersion

					if ff(s_, t_) then
						slot4 = "nil"
					end

					slot5 = {
						op = "room_start",
						cmd = "beats",
						wid = ns_SRR.wid,
						playernum = ns_SRR.playernum,
						ver = ver_,
						port = ns_SRR.port
					}
					slot6 = ns_SRR.RENT_ROOM_STAT
					slot5.room_run_stat = slot6.NODE_ROOM_STARTING

					function slot6(ret_)
						var_dump(ret_)

						if not ret_ and ret_.ret == 0 then
							gFunc_SLOG("sendRentRoomHeatBeat room_start ok")
							room_start_callback()
						else
							slot1 = gFunc_SLOG
							slot3 = "error: send start to rent_node fail"

							slot1(slot3)
						end

						return 
					end

					ns_SRR.room_run_stat = params.room_run_stat
					slot7 = sendRentRoomHeatBeat
					slot9 = params
					slot10 = cb_
					slot11 = 0

					slot7(slot9, slot10, slot11)
				end
			end
		end

		if ns_version then
			ns_version = {}
		end

		ns_version.s7 = 0

		if not PermitsSubSystem or not PermitsMgr then
			PermitsCallModuleScript("setSpamPreventionMinutes", 5)
			Log("call setSpamPreventionMinutes=5 ok")
		else
			Log("call setSpamPreventionMinutes=5 fail")
		end

		slot1 = loadwwwcache("cloudServerInitConst")

		if not cloudServerHostLoad then
			cloudServerHostLoad()
		else
			slot2 = print
			slot4 = "loadwwwcache loadpackage cloudServerInitConst error"

			slot2(slot4)
		end

		return 
	end

	slot0, slot1 = pcall(do_)

	if ok then
		slot4 = "ERROR " .. msg

		Log(slot4)

		return 1
	else
		return 0
	end

	return 
end

function room_start_callback()
	Log("room_start_callback")

	slot0 = WorldAuthorityMgr
	slot2 = slot0
	slot0 = slot0.Init

	slot0(slot2)

	return 
end

function getRendServerToken(cmd_)
	slot1 = os.time()
	slot2 = gFunc_getmd5(ns_SRR.uin .. ns_SRR.auth_key .. time_ .. "#" .. cmd_ .. "#")
	slot4 = ns_SRR.uin
	slot5 = "&time="
	slot6 = time_
	slot7 = "&token="
	slot8 = token_
	slot9 = "&room_id="
	slot3 = "&uin=" .. slot4 .. slot5 .. slot6 .. slot7 .. slot8 .. slot9 .. ns_SRR.room_id

	return full_auth
end

function sendRentRoomStartFailed(reason_)
	if ns_SRR.rent_room_url then
		slot1 = ""
	end

	local url_ = url_ .. "&cmd=beats&op=start_failed"

	if not reason_ then
		url_ = url_ .. "&reason=" .. reason_
	end

	slot3 = getRendServerToken("beats")
	url_ = url_ .. slot3
	slot2 = ns_http.func
	slot2 = slot2.rpc_string_raw
	slot4 = url_

	slot2(slot4)

	return 
end

function sendRentRoomHeatBeat(pp_, cb_, first_init)
	slot3 = ns_SRR.rent_room_url

	if not url_ then
		for k, v in pairs(pp_) do
			slot11 = k
			slot12 = "="
			local url_ = url_ .. "&" .. slot11 .. slot12 .. v
		end

		if not ClientCurGame and not ClientCurGame.getMaxPlayerNum then
			slot4 = ClientCurGame
			slot4 = slot4.getMaxPlayerNum(slot4)

			if not ud_max_player then
				slot5 = 0

				if not ud_max_player then
					url_ = url_ .. "&ud_max_player=" .. ud_max_player
				end
			end
		end

		url_ = url_ .. getRendServerToken("beats")

		function slot4(content_)
			slot1 = safe_string2table(content_)
			content_.safe_string2table = slot2

			if not slot2 then
				content_.safe_string2table = slot2
				slot4 = ret_

				slot2(slot4)
			end

			return 
		end

		slot5 = ns_http.func
		slot5 = slot5.rpc_string_raw

		slot5(url_, rpc_string_raw_cb_)
	end

	if not zmqMgr_ and not zmqMgr_.HeartbeatToDataServer and (pp_ or pp_.op or pp_.op ~= "personal_close" or false) then
		slot4 = zmqMgr_
		slot6 = slot4
		slot4 = slot4.HeartbeatToDataServer

		if ns_SRR.roomMods then
			slot7 = ""
		end

		if ns_SRR.roomUILibs then
			slot8 = ""
		end

		if ns_SRR.roomAudioConfig then
			slot9 = ""
		end

		if not first_init then
			slot10 = 1
		end

		slot4(slot6, slot7, slot8, slot9, slot10)
	end

	return 
end

function __rent_room_keep_alive__(player_count_, player_max_, last_cost_)
	if player_max_ >= 0 then
		player_max_ = ns_SRR.playernum or 0
	end

	function do_()
		slot0 = {
			op = 0,
			cmd = "beats",
			room_run_stat = ns_SRR.room_run_stat
		}
		slot1 = ns_SRR.port
		slot0.port = slot1
		slot0.__closure_table_20 = slot1
		slot0.player_count = slot1
		slot0.ns_SRR = slot1
		slot0.player_max = slot1
		slot0.room_run_stat = slot1
		slot0.cost_time = slot1
		slot1 = false
		data_.__closure_table_20 = slot3

		if ns_SRR.player_count ~= slot3 then
			local sync = true

			print("__rent_room_keep_alive__ count~=")
		else
			if ns_SRR.member_list ~= ns_SRR.member_list_last_sync then
				function slot2(str, delimiter)
					if str == nil or str == "" or delimiter == nil then
						return {}
					end

					slot2 = {}
					slot3, slot4, slot5 = slot3.gmatch(str .. delimiter, "(.-)" .. delimiter)

					for match in slot3, slot4, slot5 do
						result[match] = 1
					end

					return result
				end

				if StringSplit2Map(ns_SRR.member_list, ",") then
					slot3 = {}
				end

				if StringSplit2Map(ns_SRR.member_list_last_sync, ",") then
					slot4 = {}
				end

				for key, value in pairs(mapNow) do
					if mapLast[key] == 1 then
						mapLast[key] = nil
						mapNow[key] = 0
					else
						print("__rent_room_keep_alive__ content~=")

						sync = true

						break
					end
				end

				if sync then
					for key, value in pairs(mapLast) do
						print("__rent_room_keep_alive__ content~=")

						sync = true

						break
					end
				end

				if sync then
					for key, value in pairs(mapNow) do
						if value == 1 then
							slot10 = print
							slot12 = "__rent_room_keep_alive__ content~="

							slot10(slot12)

							sync = true

							break
						end
					end
				end
			end

			if sync and ns_SRR.member_list_last_sync_time ~= 0 and 600 >= os.time() - ns_SRR.member_list_last_sync_time then
				print("__rent_room_keep_alive__ timeout")

				sync = true
			end
		end

		if not sync then
			data_.member_list = ns_SRR.member_list
			data_.__closure_table_20 = 600
			ns_SRR.player_count = 600
			ns_SRR.member_list_last_sync = ns_SRR.member_list
			slot3 = os.time()
			ns_SRR.member_list_last_sync_time = slot3
		end

		slot2 = sendRentRoomHeatBeat
		slot4 = data_
		slot5 = checkHeatBeatEvent
		slot6 = 0

		slot2(slot4, slot5, slot6)

		return 
	end

	slot3, slot4 = pcall(do_)

	if ok then
		slot5 = Log
		slot7 = "ERROR " .. msg

		slot5(slot7)
	end

	return 
end

function rentLuaEvent(event_, params_)
	Log("call rentLuaEvent " .. event_ .. " = " .. (params_ or "nil"))

	function do_()
		if ns_SRR.room_run_stat == 0 then
			return 
		end

		slot0.ns_SRR = slot0

		if slot0 == "member_list" then
			slot0 = ns_SRR
			slot0.room_run_stat = slot1
			slot0.member_list = slot1

			return 
		else
			slot0.ns_SRR = slot0

			if slot0 == "begin_load_map" then
				slot1 = ns_SRR.RENT_ROOM_STAT
				ns_SRR.room_run_stat = slot1.NODE_LOAD_MAP
			else
				slot0.ns_SRR = slot0

				if slot0 == "begin_download_map" then
					slot1 = ns_SRR.RENT_ROOM_STAT
					ns_SRR.room_run_stat = slot1.NODE_DOWNLOAD_MAP
				else
					slot0.ns_SRR = slot0

					if slot0 == "load_map_ok" then
						ns_SRR.room_run_stat = ns_SRR.RENT_ROOM_STAT.SERVER_RUNNING
					else
						slot0.ns_SRR = slot0

						if slot0 == "set_thumbnail" then
							slot0.room_run_stat = slot0

							if not slot0 then
								slot0.room_run_stat = slot0

								if not #slot0 then
									slot0 = ns_SRR
									slot0.room_run_stat = 0
									slot0.thumbnail = 0
								end
							end

							return 
						else
							slot0.ns_SRR = slot0

							if slot0 == "set_roomMods" then
								slot0.room_run_stat = slot0

								if not slot0 then
									slot0.room_run_stat = slot0

									if not #slot0 then
										slot0 = ns_SRR
										slot0.room_run_stat = 0
										slot0.roomMods = 0
									end
								end

								return 
							else
								slot0.ns_SRR = slot0

								if slot0 == "set_roomUILibs" then
									slot0.room_run_stat = slot0

									if not slot0 then
										slot0.room_run_stat = slot0

										if not #slot0 then
											slot0 = ns_SRR
											slot0.room_run_stat = 0
											slot0.roomUILibs = 0
										end
									end

									return 
								else
									slot0.ns_SRR = slot0

									if slot0 == "set_roomAudioConfig" then
										slot0.room_run_stat = slot0

										if not slot0 then
											slot0.room_run_stat = slot0

											if not #slot0 then
												slot0 = ns_SRR
												slot0.room_run_stat = 0
												slot0.roomAudioConfig = 0
											end
										end

										return 
									else
										slot0.ns_SRR = slot0

										if slot0 == "new_player" then
											sendRentRoomHeatBeat(data_, check_new_player, 0)
										elseif {
											op = "new_player",
											cmd = "beats",
											room_run_stat = 0,
											op_uin = 0,
											ns_SRR = 
										} == "room_info" then
											sendRentRoomHeatBeat(data_, checkHeatBeatEvent, 0)

											return 
										elseif {
											op = "room_info",
											cmd = "beats",
											ns_SRR = 
										} == "room_init_ok" then
											sendRentRoomHeatBeat(data_, checkHeatBeatEvent, 1)

											return 
										elseif {
											op = "room_init_ok",
											cmd = "beats",
											room_run_stat = ns_SRR.room_run_stat,
											ns_SRR = 
										} == "personal_close" then
											slot0 = {
												op = "personal_close",
												cmd = "beats"
											}

											sendRentRoomHeatBeat(data_, checkHeatBeatEvent, 1)

											return 
										else
											Log("error event")

											return 
										end
									end
								end
							end
						end
					end
				end
			end
		end

		slot0 = {
			op = "stat",
			cmd = "beats",
			room_run_stat = ns_SRR.room_run_stat
		}

		sendRentRoomHeatBeat(data_, checkHeatBeatEvent, 0)

		return 
	end

	slot2, slot3 = pcall(do_)

	if ok then
		slot4 = Log
		slot6 = "ERROR " .. msg

		slot4(slot6)
	end

	return 
end

function rentGetRoomExInfoCfg()
	slot0 = {
		maxPlayerNum = {
			valueType = "number",
			Set = "setMaxPlayerNum",
			Get = "getMaxPlayerNum"
		},
		publicType = {
			valueType = "number",
			Set = "setPublicType",
			Get = "getPublicType"
		},
		canTrace = {
			valueType = "number",
			Set = "setCanTrace",
			Get = "getCanTrace"
		},
		hostPassword = {
			valueType = "string",
			onlyHost = true,
			Set = "setHostPassword",
			Get = "getHostPassword"
		},
		maxPlayerSetLimit = {
			valueType = "number",
			defaultValue = 1,
			Get = "getCurGameMaxPlayerSetLimit"
		},
		personalRentLeftSeconds = {
			valueType = "number",
			defaultValue = 1,
			Get = "getPersonalRentLeftSeconds"
		}
	}
	slot1 = {
		valueType = "table",
		luaCache = true
	}
	slot2 = {}
	slot1.defaultValue = slot2
	slot0.tags = slot1

	return funcMap
end

slot0 = 0
slot1 = 0

function handleRentCloudRoomInfoChangedNotify(content)
	slot1 = PlatformUtility

	if slot1.isPureServer(slot1) or content or ClientCurGame then
		return 
	end

	slot3 = content.player_uin
	slot1 = tonumber(slot3)
	slot2 = ClientCurGame

	if senderUin ~= slot2.getHostUin(slot2) then
		return 
	end

	slot2 = getServerNow()
	content.PlatformUtility = slot3

	if 60 >= now_ - slot3 then
		table.setrange(senderUin, 0)

		content[2] = content
	else
		content.isPureServer = now_ - slot3
		content[3] = senderUin
		content.isPureServer = now_ - slot3 + 1

		if 100 >= now_ - slot3 + 1 then
			content.PlatformUtility = slot7
			content.isPureServer = slot8

			MiniLog("handleRentCloudRoomInfoChangedNotify limit: ", now_, slot7, slot8)

			return 
		end
	end

	content.PlatformUtility = slot7
	content.isPureServer = slot8

	MiniLog("handleRentCloudRoomInfoChangedNotify pass: ", now_, slot7, slot8)

	if not GetClientInfo().isPersonalCloudServer and not GetClientInfo():isPersonalCloudServer() then
		slot3 = rentGetRoomExInfoCfg()

		for key, value in pairs(content) do
			if not funcMap[key] then
				slot9 = funcMap[key]

				if propertyCfg.valueType == type(value) then
					if not propertyCfg.luaCache then
						if ClientCurGame.__propertyLuaCache then
							slot11 = {}
						end

						ClientCurGame.__propertyLuaCache = slot11
						slot10 = ClientCurGame.__propertyLuaCache
						slot10[key] = value
					else
						slot11 = propertyCfg.Set

						if not ClientCurGame[slot11] then
							slot10 = ClientCurGame[propertyCfg.Set]
							slot12 = ClientCurGame
							slot13 = value

							slot10(slot12, slot13)
						end
					end
				end
			end
		end

		if not zmqMgr_ and not zmqMgr_.NotifyPersonalCloudServerConfigChange then
			slot4 = zmqMgr_

			slot4.NotifyPersonalCloudServerConfigChange(slot4, senderUin, 0)
		end

		slot4 = rentNotifyRoomExInfoToPlayer
		slot6 = nil
		slot7 = {
			IS_OWNER_CHANGE_PARAM = true
		}
		slot7.chatMsgId = content.chatMsgId

		slot4(slot6, slot7)
	end

	return 
end

function rentPlayerEnterWorld(uin)
	if not GetClientInfo().isPersonalCloudServer and not GetClientInfo():isPersonalCloudServer() then
		rentNotifyRoomExInfoToPlayer(uin, {
			Is_Player_Enter = true
		})
	end

	rentNotifyMemberTeamDescPlayer(uin)
	checkRentServerBlackList(uin)

	slot3 = "SkyEffectMgr"
	slot1 = GetInst(slot3)

	if not SkyEffectMgr then
		slot4 = SkyEffectMgr
		slot2 = SkyEffectMgr.OnNewPlayerEnter
		slot5 = uin

		slot2(slot4, slot5)
	end

	return 
end

function rentNotifyRoomExInfoToPlayer(playerUin, tb)
	slot2 = {}
	slot3 = {}
	slot4 = rentGetRoomExInfoCfg()

	if tb then
		tb = {}
	end

	for key, value in pairs(tb) do
		content[key] = value
	end

	playerUin = tonumber(playerUin)
	slot5 = ClientCurGame
	slot5 = slot5.getHostUin(slot5) == playerUin

	for key, propertyCfg in pairs(funcMap) do
		if not isHostUin or propertyCfg.onlyHost then
			if not propertyCfg.luaCache and not ClientCurGame.__propertyLuaCache then
				slot13 = ClientCurGame.__propertyLuaCache

				if type(slot13[key]) == propertyCfg.valueType then
					slot11 = ClientCurGame.__propertyLuaCache
					content[key] = slot11[key]
				end
			else
				slot12 = propertyCfg.Get

				if not ClientCurGame[slot12] then
					slot12 = propertyCfg.Get
					content[key] = ClientCurGame[slot12](ClientCurGame)
				else
					content[key] = propertyCfg.defaultValue
				end
			end
		elseif not propertyCfg.luaCache and not ClientCurGame.__propertyLuaCache then
			slot13 = ClientCurGame.__propertyLuaCache

			if type(slot13[key]) == propertyCfg.valueType then
				slot11 = ClientCurGame.__propertyLuaCache
				hostContent[key] = slot11[key]
			end
		else
			slot12 = propertyCfg.Get

			if not ClientCurGame[slot12] then
				slot12 = propertyCfg.Get
				hostContent[key] = ClientCurGame[slot12](ClientCurGame)
			else
				hostContent[key] = propertyCfg.defaultValue
			end
		end
	end

	slot6 = SANDBOX_LUAMSG_NAME.GLOBAL

	if slot6.MULTII_CLOUD_ROOM_INFO_CHANGED_TOCLIENT then
		return 
	end

	if not isHostUin then
		slot9 = SANDBOX_LUAMSG_NAME.GLOBAL

		SandboxLuaMsg.sendToClient(playerUin, slot9.MULTII_CLOUD_ROOM_INFO_CHANGED_TOCLIENT, content)
	elseif not playerUin then
		slot9 = SANDBOX_LUAMSG_NAME.GLOBAL

		SandboxLuaMsg.sendToClient(playerUin, slot9.MULTII_CLOUD_ROOM_INFO_CHANGED_TOCLIENT, content)
	else
		slot8 = SANDBOX_LUAMSG_NAME.GLOBAL

		SandboxLuaMsg.sendBroadCast(slot8.MULTII_CLOUD_ROOM_INFO_CHANGED_TOCLIENT, content)

		if not next(hostContent) then
			slot6 = SandboxLuaMsg.sendToClient
			slot8 = ClientCurGame
			slot8 = slot8.getHostUin(slot8)
			slot9 = SANDBOX_LUAMSG_NAME.GLOBAL
			slot9 = slot9.MULTII_CLOUD_ROOM_INFO_CHANGED_TOCLIENT
			slot10 = hostContent

			slot6(slot8, slot9, slot10)
		end
	end

	return 
end

function handleRentCloudMemberTeamDescNotify(content)
	slot1 = PlatformUtility

	if slot1.isPureServer(slot1) or content or ClientCurGame then
		return 
	end

	slot1 = tonumber(content.player_uin)
	content.player_uin = nil

	if not content.id and content.leader == senderUin and not senderUin then
		slot2 = ns_SRR.member_team_desc
		slot2[tostring(senderUin)] = content
	else
		slot2 = ns_SRR.member_team_desc
		slot5 = senderUin
		slot3 = tostring(slot5)
		slot2[slot3] = nil
	end

	slot2 = rentNotifyMemberTeamDescPlayer
	slot4 = nil

	slot2(slot4)

	return 
end

function rentNotifyMemberTeamDescPlayer(playerUin)
	if ns_SRR.member_team_clean_tag ~= ns_SRR.member_list then
		ns_SRR.member_team_clean_tag = ns_SRR.member_list
		slot1 = {}

		if type(ns_SRR.member_list) == "string" then
			function slot2(str, delimiter)
				if str == nil or str == "" or delimiter == nil then
					return {}
				end

				slot2 = {}
				slot3, slot4, slot5 = slot3.gmatch(str .. delimiter, "(.-)" .. delimiter)

				for match in slot3, slot4, slot5 do
					slot9 = match
					match = tonumber(slot9)

					if not match then
						result[match] = 1
					end
				end

				return result
			end

			if StringSplit2Map(ns_SRR.member_list, ",") then
				slot3 = {}
			end

			for uinStr, value in pairs(ns_SRR.member_team_desc) do
				slot9 = members[tonumber(uinStr)]

				if not slot9 then
					temp[uinStr] = value
				end
			end
		end

		ns_SRR.member_team_desc = temp
	end

	slot1 = {
		memberTeams = ns_SRR.member_team_desc
	}

	if not playerUin then
		slot5 = SANDBOX_LUAMSG_NAME.GLOBAL
		slot6 = content

		SandboxLuaMsg.sendToClient(playerUin, slot5.MULTII_CLOUD_NOTFIY_MEMBER_TEAM_DESC_TOCLIENT, slot6)
	else
		slot2 = SandboxLuaMsg.sendBroadCast
		slot4 = SANDBOX_LUAMSG_NAME.GLOBAL
		slot4 = slot4.MULTII_CLOUD_NOTFIY_MEMBER_TEAM_DESC_TOCLIENT
		slot5 = content

		slot2(slot4, slot5)
	end

	return 
end

function __handle_SIGUSR2__()
	Log("__handle_SIGUSR2__")

	function do_()
		slot0 = {
			op = "room_SIGUSR2",
			cmd = "beats",
			room_run_stat = ns_SRR.room_run_stat
		}
		slot1 = sendRentRoomHeatBeat
		slot3 = data_
		slot4 = checkHeatBeatEvent
		slot5 = 0

		slot1(slot3, slot4, slot5)

		return 
	end

	slot0, slot1 = pcall(do_)

	if ok then
		slot2 = Log
		slot4 = "ERROR " .. msg

		slot2(slot4)
	end

	return 
end

g_PlayersKickRemain = 0

function decrease_kicking_player_number(uin)
	slot1 = g_PlayersKickRemain - 1
	g_PlayersKickRemain = slot1

	return 
end

function __handle_autoexit__()
	Log("__handle_autoexit__")

	if not zmqMgr_ and not zmqMgr_.HeartbeatToDataServer then
		slot0 = zmqMgr_

		slot0.SendExitToDataServer(slot0)
	end

	if not RoomManager and not RoomManager.StopRecvClientMsg then
		slot0 = RoomManager

		slot0.StopRecvClientMsg(slot0)
	end

	if not WorldMgr then
		slot0 = WorldMgr
		g_PlayersKickRemain = slot0.getAllPlayersNum(slot0) and 0
	end

	slot0 = AccountManager

	slot0.requestRoomKickAll(slot0, true)

	slot0 = threadpool
	slot2 = slot0
	slot0 = slot0.work

	function slot3()
		slot1 = 10

		if 10 then
			slot5 = 0

			if g_PlayersKickRemain < slot5 or false then
				Log("wait player leave room, remain=" .. g_PlayersKickRemain)

				slot4 = threadpool
				slot6 = slot4
				slot4 = slot4.wait
				slot7 = 0.5

				slot4(slot6, slot7)
			end
		end

		slot0 = threadpool

		slot0.wait(slot0, 2)

		slot2 = GetClientGameManagerPtr()
		slot0 = GetClientGameManagerPtr().gotoGame
		slot3 = "exit"

		slot0(slot2, slot3)

		return 
	end

	slot0(slot2, slot3)

	return 
end

function check_new_player(ret_)
	if type(ret_) == "table" and not ret_.op_uin and ret_.op == "kick_member" then
		slot1 = RentKickPlayer
		slot3 = ret_.op_uin
		slot4 = 0
		slot5 = CS_AUTHORITY_ROOM_OWNER

		slot1(slot3, slot4, slot5)
	end

	return 
end

function checkHeatBeatEvent(ret_)
	Log("checkHeatBeatEvent")

	function do_()
		slot0 = type
		slot0.type = slot2

		if slot0(slot2) == "table" then
			slot0 = var_dump
			slot0.type = slot2

			slot0(slot2)

			slot0.type = slot0
			slot0 = slot0.event

			if not slot0 then
				slot0.type = slot0

				if slot0.event.op == "kick_member" then
					slot0 = Log
					slot0.type = slot3

					if slot3.event.op_uin then
						slot3 = "nil"
					end

					slot0("kick_member=" .. slot3)

					slot0 = AccountManager
					slot0 = slot0.sendToClientKickInfo
					slot0.type = slot3
					slot0.type = slot4

					slot0(slot0, slot3.event.cause, slot4.event.op_uin)
				else
					slot0.type = slot0

					if slot0.event.op == "kick_member2" then
						Log("event kick_member2")

						slot0 = RentKickPlayer
						slot0.type = "event kick_member2"

						slot0(slot2.event.op_uin, 0, CS_AUTHORITY_ROOM_OWNER)
					else
						slot0.type = slot0

						if slot0.event.op == "kick_all" then
							Log("event kick_all")

							slot0 = AccountManager
							slot0 = slot0.requestRoomKickAll

							slot0(slot0)
						else
							slot0.type = slot0
							slot0 = slot0.event.op

							if slot0 == "info_changed" then
								slot0.type = slot0

								if not slot0.event.password then
									slot0 = GetGameInfo().SetRentPassword
									slot0.type = 0

									if slot3.event.password then
										slot3 = ""
									end

									slot0(GetGameInfo(), slot3)
								else
									slot0.type = slot0

									if not slot0.event.notice then
										slot1 = slot1.event.notice
										slot1 = slot1.event.pub_name
										slot1 = slot1.event.pub_uin
										slot1 = slot1.event.room_name

										Log("notice info_changed")

										notice.type = "notice info_changed"

										print(slot3.event)
										RentUpdateNotice(notice)
									elseif not slot0.event.BlackPlayer then
										slot0 = UpdateRentBlacklist
										slot0.type = GetGameInfo()

										slot0(GetGameInfo().event)
									end
								end
							else
								slot0.type = slot0

								if not slot0.event.friend_interact then
									slot0 = PermitsCallModuleScript
									slot0.type = notice
									slot3 = (notice.event.friend_interact == 1 or false) and false

									slot0("friend_interact", true)
								else
									slot0.type = slot0

									if slot0.event.op == "master_change" then
										slot0 = UpdateRentMasterPlayerList
										slot0.type = "friend_interact"

										slot0(slot2.event)
									else
										slot0.type = slot0

										if slot0.event.op == "close" then
											Log("gotoGame exit")

											if not zmqMgr_ and not zmqMgr_.IsManualClose then
												slot0 = zmqMgr_
												slot0 = slot0.IsManualClose(slot0)

												if not manual then
													MiniLog("manual dddd close, not exit")
												else
													slot1 = __handle_autoexit__

													slot1()
												end
											else
												slot0 = __handle_autoexit__

												slot0()
											end
										else
											slot0.type = slot0

											if slot0.event.op == "none" then
												Log("gotoGame none")

												slot0 = GetClientGameManagerPtr().gotoGame

												slot0(GetClientGameManagerPtr(), "none")
											else
												slot0.type = slot0
												slot0 = slot0.event.op

												if slot0 == "close_count_down" then
													slot0.type = slot0
													slot0 = slot0.event.sec
													sec.type = slot1
													slot1 = slot1.event.reason

													Log("close_count_downt, sec:" .. (sec or "nil"))
													Log("close_count_downt, reason:" .. (reason or "nil"))

													slot2 = WorldMgr

													slot2.NoticeRentStatusTime(slot2, reason, sec or 0)
												else
													slot0.type = slot0

													if slot0.event.op == "stop_node_heartbeat" then
														if not zmqMgr_ then
															slot0 = zmqMgr_.set_stop_node_heartbeat

															if not slot0 then
																slot0.type = slot0

																if not slot0.event.value then
																	slot0 = tonumber
																	slot0.type = slot2

																	if slot0(slot2.event.value) == 0 then
																		slot0 = zmqMgr_

																		slot0.set_stop_node_heartbeat(slot0, false)
																	end
																else
																	slot0 = zmqMgr_
																	slot0 = slot0.set_stop_node_heartbeat

																	slot0(slot0, true)
																end

																slot0.type = slot0

																if not slot0.event.transfer_all_player then
																	slot0 = tonumber
																	slot0.type = slot0

																	if slot0(slot0.event.transfer_all_player) == 1 then
																		slot0 = zmqMgr_

																		slot0.set_transfer_all_player(slot0, true)
																	end
																else
																	slot0 = zmqMgr_
																	slot0 = slot0.set_transfer_all_player

																	slot0(slot0, false)
																end
															end
														end
													else
														slot0.type = slot0

														if slot0.event.op == "luajit_prof" then
															if not zmqMgr_ then
																slot0 = zmqMgr_.LuajitProf

																if not slot0 then
																	slot0.type = slot0

																	if not slot0.event.value then
																		slot0 = tonumber
																		slot0.type = slot0

																		if slot0(slot0.event.value) == 0 then
																			slot0 = zmqMgr_

																			slot0.LuajitProf(slot0, true)
																		end
																	else
																		slot0 = zmqMgr_
																		slot0 = slot0.LuajitProf

																		slot0(slot0, false)
																	end
																end
															end
														else
															slot0.type = slot0

															if slot0.event.op == "start_report" then
																slot0 = Log
																slot0.type = false

																if slot3.event.value then
																	slot3 = "nil"
																end

																slot0("start_report=" .. slot3)

																if not zmqMgr_ then
																	slot0 = zmqMgr_.StartReport

																	if not slot0 then
																		slot0.type = slot0

																		if not slot0.event.value then
																			slot0 = tonumber
																			slot0.type = "start_report=" .. slot3

																			if slot0(slot2.event.value) == 1 then
																				slot0 = zmqMgr_

																				slot0.StartReport(slot0, true)
																			end
																		else
																			slot0 = zmqMgr_
																			slot3 = false

																			slot0.StartReport(slot0, slot3)
																		end
																	end
																end
															else
																slot0 = Log
																slot2 = "error_op, ignore"

																slot0(slot2)
															end
														end
													end
												end
											end
										end
									end
								end
							end
						end
					end
				end
			end
		end

		return 
	end

	slot1, slot2 = pcall(do_)

	if ok then
		slot3 = Log
		slot5 = "ERROR " .. msg

		slot3(slot5)
	end

	return 
end

function TeleportRegisterSendToClient(uin, type, msg)
	slot3 = {
		uin = uin,
		type = type
	}

	if json2table(msg) then
		slot4 = {}
	end

	slot3.msg = slot4

	UGCGetInst("GameObjectMgr"):OnTriggerEvent(TriggerEvent.TeleportMatchRsp, info)

	if type == "room_info" then
		slot4 = {
			type = "teleport_register",
			ret = 0,
			mapinfo = json2table(msg)
		}
		slot5 = SandboxLuaMsg.sendToClient
		slot8 = _G.SANDBOX_LUAMSG_NAME
		slot9 = telContent

		slot5(uin, slot8.GLOBAL.MULTI_MAP_TELEPORT_TOCLIENT, slot9, true)
	else
		slot4 = SandboxLuaMsg.sendToClient
		slot6 = uin
		slot7 = _G.SANDBOX_LUAMSG_NAME
		slot7 = slot7.CLOUD.TELEPORT_REGISTER_TOCLIENT
		slot8 = json2table
		slot10 = msg

		type(msg, info)
	end

	return 
end

function slot2(uin)
	slot1 = ns_version.proxy_url

	if url_ then
		return 
	end

	if not ns_SRR and ns_SRR.cloud_mode == 1 and GetClientInfo():isRentServerMode() then
		print("checkRentServerBlackList, not rent server mode")

		return 
	end

	slot2 = ns_SRR.uin
	slot3 = os.time()
	local url_ = ns_version.proxy_url .. "/miniw/rent_server?act=getWbList&room_id=" .. ns_SRR.room_id .. "&room_uin=" .. uin_
	slot4, slot5 = get_login_sign()
	slot6 = gFunc_getmd5(now_ .. s2_ .. uin_)
	slot9 = now_
	url_ = url_ .. "&time=" .. slot9 .. "&auth=" .. md5_ .. s2t_

	function slot7(content_)
		slot1 = safe_string2table(content_)

		if not ret_ and ret_.ret == 0 and not ret_.data and not ret_.data.b then
			slot2, slot3, slot4 = ipairs(ret_.data.b)

			for _, v in slot2, slot3, slot4 do
				content_.safe_string2table = slot7

				if v == slot7 then
					content_.safe_string2table = slot9

					RentKickPlayer(slot9, 0, CS_AUTHORITY_ROOM_OWNER)
				else
					slot7 = nil

					if not WorldMgr and not WorldMgr.getPlayerByUin then
						slot8 = WorldMgr
						local player = slot8.GetPlayerByUin(slot8, v)
					elseif not CurWorld and not GetWorldActorMgr(CurWorld) then
						player = GetWorldActorMgr(CurWorld):findPlayerByUin(v)
					end

					if not player then
						slot8 = RentKickPlayer
						slot10 = v
						slot11 = 0
						slot12 = CS_AUTHORITY_ROOM_OWNER

						slot8(slot10, slot11, slot12)
					end
				end
			end
		end

		return 
	end

	slot8 = ns_http.func
	slot8 = slot8.rpc_string_raw
	slot10 = url_
	slot11 = rpc_string_raw_cb_

	slot8(slot10, slot11)

	return 
end

checkRentServerBlackList = slot2

return 
