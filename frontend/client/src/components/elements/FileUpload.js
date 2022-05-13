import React from 'react'

import "../../css/bootstrap.min.css"
import "../../css/global.css"

export default function FileUpload(props)
{
    const { image, caption, style  } = props;

    function imgError(image) 
    {

        // var svgNS = "http://www.w3.org/2000/svg";
        // var newText = document.createElementNS(svgNS,"text");
        // newText.setAttributeNS(null,"x",0);     
        // newText.setAttributeNS(null,"y",0); 
        // newText.setAttributeNS(null,"font-size","100");
        
        // var textNode = document.createTextNode("UWU");
        // newText.appendChild(textNode);
        // image.appendChild(newText);

        // image.onerror = "";
        // // image.src = document.getElementById("g");
        // console.log(type);
        return true;
    }

    return (
        <div className="file-container" style={style} loading="lazy">
                <img src={image} width={"100%"} onError={imgError} loading="lazy" />
                <div className="caption">{caption}</div>
        </div>
    )
}
