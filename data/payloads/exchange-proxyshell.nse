local http = require "http"
local nmap = require "nmap"
local shortport = require "shortport"
local strbuf = require "strbuf"

description = [[
Check for Exchange Server CVE-2021-34473
by trying to access OWA as NT AUTHORITY\SYSTEM
Known issues - requires a valid SSL certificate if using SSL/TLS
]]

---
--@output
--PORT    STATE SERVICE
-- 443/tcp open  https
-- |_http-vuln-exchange-proxyshell: True

author = "Kevin Beaumont"
license = "GPLv3"
categories = {"default", "discovery", "safe", "exploit"}

portrule = shortport.http

local last_len = 0

action = function(host, port)
  local dis_count, noun
  options = {redirect_ok = false}
  local answer = http.get(host, port, "/autodiscover/autodiscover.json?@test.com/owa/?&Email=autodiscover/autodiscover.json%3F@test.com", options)

  if answer.status == 302 then
      return "True"
  else
      return "False"
  end

  local v_level = nmap.verbosity() + (nmap.debugging()*2)
  local output = strbuf.new()
  local detail = 15

end
