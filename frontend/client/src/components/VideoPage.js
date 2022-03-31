import React, { Component } from 'react';
import { Player, ControlBar } from 'video-react';
// import { button } from 'reactstrap';

// Render a YouTube video player

const sources = {
  sintelTrailer: 'http://192.168.1.149:721/static/v/fall2.mp4',
  bunnyTrailer: 'http://192.168.1.149:721/static/v/fall3.avi',
  bunnyMovie: 'http://localhost:721/static/v/rick_and_mort_01.mp4'
};

export default class VideoPage extends Component {
  constructor(props, context) {
    super(props, context);

    this.state = {
      source: sources.bunnyMovie
    };

    this.play = this.play.bind(this);
    this.pause = this.pause.bind(this);
    this.load = this.load.bind(this);
    this.changeCurrentTime = this.changeCurrentTime.bind(this);
    this.seek = this.seek.bind(this);
    this.changePlaybackRateRate = this.changePlaybackRateRate.bind(this);
    this.changeVolume = this.changeVolume.bind(this);
    this.setMuted = this.setMuted.bind(this);
  }

  componentDidMount() {
    // subscribe state change
    this.player.subscribeToStateChange(this.handleStateChange.bind(this));
  }

  setMuted(muted) {
    return () => {
      this.player.muted = muted;
    };
  }

  handleStateChange(state) {
    // copy player state to this component's state
    this.setState({
      player: state
    });
  }

  play() {
    this.player.play();
  }

  pause() {
    this.player.pause();
  }

  load() {
    this.player.load();
  }

  changeCurrentTime(seconds) {
    return () => {
      const { player } = this.player.getState();
      this.player.seek(player.currentTime + seconds);
    };
  }

  seek(seconds) {
    return () => {
      this.player.seek(seconds);
    };
  }

  changePlaybackRateRate(steps) {
    return () => {
      const { player } = this.player.getState();
      this.player.playbackRate = player.playbackRate + steps;
    };
  }

  changeVolume(steps) {
    return () => {
      const { player } = this.player.getState();
      this.player.volume = player.volume + steps;
    };
  }

  changeSource(name) {
    return () => {
      this.setState({
        source: sources[name]
      });
      this.player.load();
    };
  }

  render() {
    return (
      <div>
        <Player
          ref={player => {
            this.player = player;
          }}
          autoPlay
        >
          <source src={this.state.source} />
          <ControlBar autoHide={false} />
        </Player>
        <div className="py-3">
          <button onClick={this.play} className="mr-3">
            play()
          </button>
          <button onClick={this.pause} className="mr-3">
            pause()
          </button>
          <button onClick={this.load} className="mr-3">
            load()
          </button>
        </div>
        <div className="pb-3">
          <button onClick={this.changeCurrentTime(10)} className="mr-3">
            currentTime += 10
          </button>
          <button onClick={this.changeCurrentTime(-10)} className="mr-3">
            currentTime -= 10
          </button>
          <button onClick={this.seek(50)} className="mr-3">
            currentTime = 50
          </button>
        </div>
        <div className="pb-3">
          <button onClick={this.changePlaybackRateRate(1)} className="mr-3">
            playbackRate++
          </button>
          <button onClick={this.changePlaybackRateRate(-1)} className="mr-3">
            playbackRate--
          </button>
          <button onClick={this.changePlaybackRateRate(0.1)} className="mr-3">
            playbackRate+=0.1
          </button>
          <button onClick={this.changePlaybackRateRate(-0.1)} className="mr-3">
            playbackRate-=0.1
          </button>
        </div>
        <div className="pb-3">
          <button onClick={this.changeVolume(0.1)} className="mr-3">
            volume+=0.1
          </button>
          <button onClick={this.changeVolume(-0.1)} className="mr-3">
            volume-=0.1
          </button>
          <button onClick={this.setMuted(true)} className="mr-3">
            muted=true
          </button>
          <button onClick={this.setMuted(false)} className="mr-3">
            muted=false
          </button>
        </div>
        <div className="pb-3">
          <button onClick={this.changeSource('sintelTrailer')} className="mr-3">
            Sintel teaser
          </button>
          <button onClick={this.changeSource('bunnyTrailer')} className="mr-3">
            Bunny trailer
          </button>
          <button onClick={this.changeSource('bunnyMovie')} className="mr-3">
            Bunny movie
          </button>
        </div>
        <div>State</div>
        {/* <pre>
          <PrismCode className="language-json">
            {JSON.stringify(this.state.player, null, 2)}
          </PrismCode>
        </pre> */}
      </div>
    );
  }
}
