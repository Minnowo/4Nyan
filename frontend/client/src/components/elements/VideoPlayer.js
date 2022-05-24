
import React from "react";

import Hls from "hls.js";
import dashjs from 'dashjs'

// import 'dash.js'

import "../../css/video.css"


export default function VideoPlayer(props)
{
    const playerRef = React.useRef(null);  

    React.useEffect(() => 
    {
        if(!playerRef)
        {
            alert("no player found. use a modern browser for video.");
            return;
        }
            
        const hlsUrl = props.m3u8;
        const video = playerRef.current;

        const player = dashjs.MediaPlayer().create();

        player.initialize(video, hlsUrl, true);
        // // If HLS is natively supported, let the browser do the work!
        // // i have no idea if this actually works because it always uses HLS xd 
        // if (video.canPlayType("application/vnd.apple.mpegurl"))
        // {
        //     video.src = hlsUrl;

        //     video.addEventListener("loadedmetadata", function() 
        //     { 
        //         video.play(); 
        //     });
        //     return;
        // } 

        // // If the browser supports MSE, use hls.js to play the video
        // if (Hls.isSupported()) 
        // {
        //     // This configuration is required to insure that only the
        //     // viewer can access the content by sending a session cookie
        //     // to api.video service
        //     var hls = new Hls();
            
        //     hls.loadSource(hlsUrl); // set the m3u8 url
        //     hls.attachMedia(video); // attach video player?

        //     if(props.autoPlay)
        //     {
        //         hls.on(Hls.Events.MANIFEST_PARSED, function() 
        //         { 
        //             video.play(); 
        //         });
        //     }

        //     hls.on(Hls.Events.ERROR, function (event, data) 
        //     {
        //         if (data.fatal) 
        //         {
        //           switch (data.type) 
        //           {
        //             case Hls.ErrorTypes.NETWORK_ERROR:
        //               // try to recover network error
        //               console.log('fatal network error encountered, try to recover');
        //               hls.startLoad();
        //               break;
                  
        //               case Hls.ErrorTypes.MEDIA_ERROR:
        //               console.log('fatal media error encountered, try to recover');
        //               hls.recoverMediaError();
        //               break;
                  
        //               default:
        //               // cannot recover
        //               hls.destroy();
        //               break;
        //           }
        //         }
        //       });
        // } 
    }, []);



    return (
        <div>
         
            <video className="video" 
                    controls 
                    ref={playerRef} 
                    autoPlay={props.autoPlay}></video>
        </div>
    );
}


