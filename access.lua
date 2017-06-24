local cjson = require "cjson.safe"

local res = ngx.location.capture("/@@addheader")
if not res then
    ngx.exit(500)
end

local headers = cjson.decode(res.body)
for k, v in pairs(headers) do
    ngx.req.set_header(k, v)
end
