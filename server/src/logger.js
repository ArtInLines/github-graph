
const logApiRequests = true
const requestLogger = (req,res,next) => {
    if(req.method !== "OPTIONS" && logApiRequests){
      console.log("--------------------------------------------------")
      console.log("New request at: ", new Date().toDateString(), new Date().toTimeString())
      console.log("Type:", req.method)
      console.log("Requested URL:", req.originalUrl)
      next()
    }
    else if(logApiRequests){
      console.log("\n")
      console.log("PRE-FLIGHT OPTIONS REQUEST");
      console.log("setting Access-Control-Max-Age to 600 for "+ req.originalUrl)
      res.set('Access-Control-Max-Age', 600)
      next()
    }
    else{
      next()
    }
}

module.exports={logger: requestLogger}