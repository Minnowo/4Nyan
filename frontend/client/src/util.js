




function objectEmpty(obj) 
{
    for (var i in obj) 
        return false;
        
    return true;
}


export default objectEmpty