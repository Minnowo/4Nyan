import React, { Component } from "react";

import Hls from "hls.js";

export default class Video extends Component {
  
  state = {
    "m3u8" : this.props.m3u8,
    "autoPlay" : false
  }

  componentDidMount () 
  {

    if(!this.player)
    {
      alert("no player found. use a modern browser for video.");
      return;
    }
      
    var hlsUrl = this.state.m3u8;
    var video = this.player;

    // If HLS is natively supported, let the browser do the work!
    // i have no idea if this actually works because it always uses HLS xd 
    if (video.canPlayType("application/vnd.apple.mpegurl")) 
    {
      video.src = hlsUrl;
      video.addEventListener("loadedmetadata", function() { video.play(); });
      return;
    } 


    // If the browser supports MSE, use hls.js to play the video
    if (Hls.isSupported()) 
    {
      // This configuration is required to insure that only the
      // viewer can access the content by sending a session cookie
      // to api.video service
      var hls = new Hls({ xhrSetup: function(xhr, url) { xhr.withCredentials = true; }});
        
      hls.loadSource(hlsUrl); // set the m3u8 url
      hls.attachMedia(video); // attach video player?

      if(this.state.autoPlay)
      {
        hls.on(Hls.Events.MANIFEST_PARSED, function() { video.play(); });
      }
    } 
  }

  render() 
  {    
      return (
        <div>
          {/* what is this doing?? where does this.player get set? is it here? what does 'controls' mean??? */}
          <video controls onClick={this._onTouchInsidePlayer} ref={player => (this.player = player)} autoPlay={this.state.autoPlay}/>
        </div>
      );
    }
}