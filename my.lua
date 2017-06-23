local http = require "resty.http"
local cjson = require "cjson.safe"

local httpc = http.new()

-- The generic form gives us more control. We must connect manually.
--httpc:set_timeout(500)
--httpc:connect("127.0.0.1", 80)

-- And request using a path, rather than a full URI.

local sr = "http://127.0.0.1:5000" .. "/api/v1.0/status"
local res, err = httpc:request_uri(sr)
jres,err = cjson.decode(res.body)
ngx.log(ngx.NOTICE, "get return from q: " .. jres["status"])
--ngx.req.set_header("qstatus", jres["status"])
ngx.req.set_header("qstatus", "running")

local dr = "http://127.0.0.1:5000" .. ngx.var['request_uri']
ngx.log(ngx.NOTICE, "xxxx: " .. dr)
local hdrs = { ["ceo"] = "shuxin" }
hdrs['qstatus'] = jres["status"]

for k, v in pairs(ngx.req.get_headers()) do
 hdrs[k] = v
 --ngx.log(ngx.NOTICE, "WTF : " .. k .. ": " .. v)
end

local res, err = httpc:request_uri(dr, { headers = hdrs })
if not res then
    ngx.status = 400
    ngx.header["yangzong"] = "xxxx"
    ngx.say ("hahahha" .. err)
else
    ngx.header["content-type"] = "text/plain"
    ngx.header["yangzong"] = "yyyyy"
    ngx.say(res.body)
end
