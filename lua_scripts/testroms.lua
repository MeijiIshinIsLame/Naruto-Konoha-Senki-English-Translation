-- Path to list.txt (same folder as script)
local file_path = "list.txt"

-- Try to open the file
local f = io.open(file_path, "r")

-- Read and log each line
for line in f:lines() do
    console:log(line)
end

f:close()
