# midicontrol_supercollider

```supercollider
SynthDef("sine", {
	arg freq = 440, amp = 0.2, parFreq=0, pan2Freq=0, pan=0,
	vibratoFreq=3, vibratoDepth=0, actave=1, reverb=0, ice=0, distort=0;
	var sig, out=0, chain, in, z, y, oct, left, right, mod;
	sig = SinOsc.ar(actave*freq*(1+((LFPar.ar(vibratoFreq)+1)*(vibratoDepth/50))), 0, amp);
	// distort
	mod = CrossoverDistortion.ar(sig, amp: 0.2, smooth: 0.01);
	mod = mod + (0.1 * distort * DynKlank.ar(`[[60,61,240,3000 + SinOsc.ar(62,mul: 100)],nil,[0.1, 0.1, 0.05, 0.01]], sig));
	mod = (mod.cubed * 8).softclip * 0.5;
	sig = SelectX.ar(distort, [sig, mod]);
	// tremoro
	sig = if(
		parFreq>0.1,
		sig*LFPar.ar(parFreq),
		if(
			LFPar.ar(parFreq)>0,
			sig*(LFPar.ar(parFreq) + (1-(LFPar.ar(parFreq))*((1-(parFreq*10))))),
			sig*(LFPar.ar(parFreq) + (-1-(LFPar.ar(parFreq))*((1-(parFreq*10))))),
		)
	);
	// panning
	sig = if(
		pan2Freq>0.1,
		Pan2.ar(sig, LFPar.ar(pan2Freq)),
		Pan2.ar(sig, LFPar.ar(pan2Freq)*pan2Freq*10)
	);
	// reverb
	z = DelayN.ar(sig, 0.048);
	y = Mix.ar(Array.fill(7,{ CombL.ar(z, 0.1, 1, 15) }));
	32.do({ y = AllpassN.ar(y, 0.050, [0.050.rand, 0.050.rand], 1) });
	oct = 1.0 * LeakDC.ar( abs(y) );
	y = SelectX.ar(ice, [y, ice * oct, DC.ar(0)]);
	sig = sig + (0.2*y*reverb);
	sig = sig * 0.1;
    Out.ar(out, sig);
}, [0.2, 1, 1, 1, 1, 1, 1, 1, 10, 10, 10]).add;
```

# 使うシンセ

## mode: 0

`sine`を1~8チャンネルで使用

## mode: 1

- 1チャンネル
  - `sine`のfreq`640.487/4`
- 2チャンネル
  - `sine`のfreq`570.609/4`
- 3チャンネル
  - `sea`
- 4チャンネル
  - `deapsea`
- 5チャンネル
  - `rain`
- 6チャンネル
  - `river`
- 7チャンネル
  - `forest`
- 8チャンネル
  - なし
