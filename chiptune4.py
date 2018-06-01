"""
Some issues...
- when using "ALL" and/or "NA" pitch tables are still available (and volume envelopes for "ALL") but it's up to the user to not use them
- you can use them but the sound might be funky
- it might be helpful to have "custom" durations

A complete redesign of the chiptune architecture
Based on wavetables as a way to control everything more precisely
Custom waveforms, custom envelops, can create pitch/volume envelops easily like on Famitracker
Pulse duty cycles will not be changeable on the fly like on Famitracker
    
API
    - use .cfg extension?
    - cmd line argument is song name - sets song name in API and uses it to open config file
        - or do we use separate folders?  contains config and song files? helps with clutter?
        - can save the .wav there too? 
        
When using drums:
    - use "NA" for frequency - this makes the tw equal to 1 and the program will use all samples in the file
    - make sure duration is long enough for the envelope
    - don't use .pit files
    - make sure volume envelope ends in a 0
    
When using a sample:
    - use "NA" for frequency - this makes the tw equal to 1 and the program will use all samples in the file
    - use "ALL" for duration - this makes sure all samples in the wave table are used
    - if a sample is allowed to be cutoff then use proper duration
    - don't use .vol or .pit files
    - the instrument might not be synced with the rest of the instruments so a separate instrument might be needed
      for each iteration if a sample is to be used multiple times.  This could make things messy.  Or the file needs
      to be tailored to get the desired length.  Or a proper duration needs to be picked - instead of using "ALL"
"""
import array
import freq
import wave
import math

class Chiptune:

    def __init__(self, name, resolution, sample_rate, bpm, songfile):
        ## TODO: error checking
        # set data members
        self._name = name + '.wav'
        self._resolution = int(resolution)
        self._sample_rate = int(sample_rate)
        self._bpm = int(bpm)
        self._song_file_path = 'C:/Python/chiptune/song/' + songfile
        self._instruments = []
        
    def make_instrument(self, name, volume, wavetable):
        ## TODO:  error checking
        inst = Instrument()
        inst._name = name
        inst._volume = float(volume)
        inst._wavetable_path = 'C:/Python/chiptune/waves/' + wavetable # for now I know on my machine this is the path, might want to generalize it in the future
        inst._vfx = []
        inst._pfx = []
        self._instruments.append(inst)
        
    def make_song(self):

        # empty song array
        song = array.array('h')
        
        # handy dandy lambdas
        QUARTER = lambda: 15  / self._bpm
        HALF =    lambda: 30  / self._bpm
        THREE_QTR = lambda: 45 / self._bpm
        ONE =     lambda: 60  / self._bpm
        ONE_QTR = lambda: 75  / self._bpm
        ONE_HALF = lambda: 90 / self._bpm
        ONE_THREE_QTR = lambda: 105 / self._bpm
        TWO =     lambda: 120 / self._bpm
        TWO_QTR = lambda: 135 / self._bpm
        TWO_HALF = lambda: 150 / self._bpm
        TWO_THREE_QTR = lambda: 165 / self._bpm
        THREE =   lambda: 180 / self._bpm
        THREE_QTR = lambda: 195 / self._bpm
        THREE_HALF = lambda: 210 / self._bpm
        THREE_THREE_QTR = lambda: 225 / self._bpm 
        FOUR =    lambda: 240 / self._bpm
        ALL =     lambda: wl  / self._sample_rate

        for inst in self._instruments:
            # initialize variables
            pa = 0 # phase accumulator
            vol = inst._volume
            song_index = 0
            release_samples = 0
            
            # create wavetable
            w = open(inst._wavetable_path)
            wt = w.read().split('\n') # wave table
            wl = len(wt) # wave length
            min_freq = self._sample_rate / wl
            w.close()
                
            # create note table
            notes = []
            s = open(self._song_file_path)
            sp = s.read().split('\n')
            inst_list = sp[0].split('|')
            for i in inst_list:
                inst_list[inst_list.index(i)] = i.strip()
            inst_index = inst_list.index(inst._name)
            for line in sp[1:]:
                notes.append(line.split('|')[inst_index].strip())
            s.close()
            
            for n in notes:
                if n == '':
                    continue
                note = n.split(',')
                
                # reset all _index values for _vfx and _pfx
                for vfx in inst._vfx:
                    vfx._index = 0
                for pfx in inst._pfx:
                    pfx._index = 0

                # note frequency
                base_freq = getattr(freq, note[0])
                
                # set rest flag if the note is a rest
                if base_freq == 0:
                    rest = True
                    # reset the phase accumulator so instrument resumes at beginning of wave table 
                    pa = 0
                else:
                    rest = False
                    
                # tuning word 
                if base_freq == 1:
                    # set to 1 if we need to play all samples
                    base_tw = 1
                    pa = 0
                else:
                    base_tw = base_freq / min_freq
                
                # note duration in samples
                duration = int(self._sample_rate * eval(note[1])())
                
                # check for effects
                if len(note) == 3:
                    effects = note[2].strip().split(';')
                    for effect in effects:
                        if effect[-4:] == '.vol':
                            # (api should have made sure that the file exists)
                            # check if effect is already being used
                            new_vfx = True
                            for vfx in inst._vfx:
                                if vfx._name == effect:
                                    # delete vfx from array
                                    del inst._vfx[inst._vfx.index(vfx)]
                                    new_vfx = False
                            if new_vfx:
                                # create Effect object
                                veff = Effect()
                                # set _name and _index attributes
                                veff._name = effect
                                veff._index = 0
                                veff._release = False
                                # parse and create _table array
                                # open file
                                path = 'C:/Python/chiptune/envelope/' + effect
                                e = open(path)
                                veff._table = e.read().split('\n')
                                # look for ':' and set sustain index
                                if ':' in veff._table:
                                    veff._susindex = veff._table.index(':')
                                    # check if there is a release section
                                    if veff._table[-1] != ':':
                                        veff._release = True
                                else:
                                    veff._susindex = -1
                                inst._vfx.append(veff)
                                e.close()

                        elif effect[-4:] == '.pit':
                            # check if effect is already being used
                            new_pfx = True
                            for pfx in inst._pfx:
                                if pfx._name == effect:
                                    # delete pfx from array
                                    del inst._pfx[inst._pfx.index(pfx)]
                                    new_pfx = False
                            if new_pfx:
                                # create Effect object
                                peff = Effect()
                                # set _name and _index attributes
                                peff._name = effect
                                peff._index = 0
                                peff._release = False
                                # parse and create _table array
                                # open file
                                path = 'C:/Python/chiptune/pitch/' + effect
                                p = open(path)
                                peff._table = p.read().split('\n')
                                # look for ':' and set sustain index
                                if ':' in peff._table:
                                    peff._susindex = peff._table.index(':')
                                else:
                                    peff._susindex = -1
                                inst._pfx.append(peff)
                                p.close()
                
                done = False
                i = 0
                song_index -= release_samples
                release_samples = 0
                
                #for i in range(0, duration):
                while not done:                     
                    if rest:
                        vmod = 0
                        wave_sample = 0
                    else:
                        # round wave index and pull value from wavetable
                        wave_sample = float(wt[round(pa)])
                        # get the volume modulation value
                        vmod = 1
                        for env in inst._vfx:
                            # found a sustain symbol
                            if env._table[env._index] == ':':
                                # at the first one, increment the index and continue
                                if env._index == env._susindex:
                                    env._index += 1
                                # at the second one, go back to the beginning of the sustain
                                else:
                                    env._index = env._susindex + 1
                            vmod *= float(env._table[env._index])
                            env._index += 1
                            # if we're at the end and there's no sustain, always grab the final value until the end of the note
                            if env._index == len(env._table):
                                env._index -= 1
                        
                    # add value to array
                    sample = int(wave_sample * vol * vmod)
                    if song_index == len(song):
                        song.append(sample)
                    else:
                        song[song_index] += sample
                    song_index += 1
                    
                    # get the pitch modulation value
                    pmod = 1
                    if not rest:
                        for env in inst._pfx:
                            # found a sustain symbol
                            if env._table[env._index] == ':':
                                # at the first one, increment the index and continue
                                if env._index == env._susindex:
                                    env._index += 1
                                # at the second one, go back to the beginning of the sustain
                                else:
                                    env._index = env._susindex + 1
                            pmod *= float(env._table[env._index])
                            env._index += 1
                            # if we're at the end and there's no sustain, always grab the final value until the end of the note
                            if env._index == len(env._table):
                                env._index -= 1

                    tw = base_tw * pmod
                    
                    # add tuning word to wave index
                    pa += tw
                    if pa > wl - 1:
                        pa -= wl
                    
                    # check if we're done                    
                    i += 1
                    if i == duration:
                        done = True
                        if not rest:
                            release_samples = 0 # probably unnecessary
                            for vfx in inst._vfx:
                                if vfx._release:
                                    done = False
                                    # find end of sustain - second ':'
                                    for j in range(-1, -len(vfx._table), -1):
                                        if vfx._table[j] == ':':
                                            sustain_end = len(vfx._table) + j + 1 # add 1 to get us past the ':'
                                            break
                                    # use the previous sustain value (at _index - 1) to find start of release
                                    if vfx._table[vfx._index-1] == ':':
                                        # we're at the start of the sustain so just use that value
                                        last_val = float(vfx._table[vfx._index])
                                    else:
                                        last_val = float(vfx._table[vfx._index-1])
                                    # go through release until a value <= to last sustain value found
                                    for j in range(sustain_end, len(vfx._table)):
                                        if float(vfx._table[j]) <= last_val:
                                            # set index to that value
                                            vfx._index = j
                                            # calculate remaining samples in envelope - this is the release samples in this envelope
                                            env_rs = len(vfx._table) - j # (this step can never be skipped, right?)
                                            break
                                    # compare against current release_samples value, use smallest non-zero value
                                    if release_samples > 0:
                                        release_samples = min(release_samples, env_rs)
                                    else:
                                        release_samples = env_rs
                                    # the one assumption of this module is that releases are monotonically decreasing functions that end at 0

                    elif i == duration + release_samples:
                        done = True        
        
        # create wav file
        wavfile = wave.open(self._name, 'w')
        wavfile.setparams((1, int(self._resolution / 8), self._sample_rate, 0, "NONE", "uncompressed"))
        wavfile.writeframes(song.tostring())
        wavfile.close()
    

# empty classes used as a struct        
class Instrument:
    pass

class Effect:
    pass
    
'''
Unused code
'''

#from scipy.signal import butter, lfilter, freqz

''' make_instrument '''
#        if envelope == '':
#            inst._envelope_path = 'none'
#        else:
#            inst._envelope_path = 'C:/Python/chiptune/envelope/' + envelope
#        if pitchtable == '':
#            inst._pitchtable_path = 'none'
#        else:
#            inst._pitchtable_path = 'C:/Python/chiptune/pitch/' + pitchtable

''' make_song '''
#            # create envelope and time division counter
#            has_release = False
#            if inst._envelope_path == 'none':
#                use_envelope = False
#           else:
#                use_envelope = True
#                e = open(inst._envelope_path)
#                # envelope time division in samples
#                td_string = e.readline().split('=')[1].strip()
#                if td_string == '0' or td_string == '':
#                    env_td = 1
#                else:
#                    env_td = round( float(td_string) / 1000.0 * self._sample_rate )
#                    if env_td < 1:
#                        env_td = 1
#                # create envelope list
#                env = e.read().split('\n')
#                # look for ':' and set sustain index
#                if ':' in env:
#                    env_sustain_index = env.index(':')
#                    # check if there is a release section
#                    if env[-1] != ':':
#                        has_release = True
#                else:
#                    env_sustain_index = -1
#                e.close()
#                
#            # create pitch table and time division counter
#            if inst._pitchtable_path == 'none':
#                use_pitchtable = False
#            else:
#                use_pitchtable = True
#                p = open(inst._pitchtable_path)
#                td_string = float(p.readline().split('=')[1].strip())
#                if td_string == '0' or td_string == '':
#                    pitch_td = 1
#                else:
#                    pitch_td = round( float(td_string) / 1000.0 * self._sample_rate )
#                    if pitch_td < 1:
#                        pitch_td = 1
#                # create pitchtable list
#                pitch = p.read().split('\n')
#                # look for : and set sustain index
#                if ':' in pitch:
#                    pitch_sustain_index = pitch.index(':')
#                else:
#                    pitch_sustain_index = -1
#                p.close()

#                # envelope/pitchtable variables
#                if use_envelope:
#                    env_index = 0
#                    env_counter = env_td
#                if use_pitchtable:
#                    pitch_index = 0
#                    pitch_counter = pitch_td
#                    
#                # modulation variables
#                vol_mod_env = 1
#                vol_mod_fx = 1  ## --> should this carry over on each note?  probably?
#                freq_mod_pt = 1
#                freq_mod_fx = 1
                
#                update_incrementer = False

#                begin_period = True

#                use_release = False

#                    # if beginning of a wave apply effects
#                    if begin_period:
#                        """
#                        Effects to add:
#                        - tremolo       (T)
#                        - volume slide  (VSU/VSD)
#                        - vibrato       (V)
#                        - portamento    (P)
#                        - pitch slide   (PSU/PSD)
#                        - mute delay?   (MD)
#                        - echo          (E)
#                        - volume change (VC)  X
#                        - bpm change    (BPM) X
#                        """
#                        ## volume modulation effects...
#                        ##vol_mod_fx = ...
#                        ## frequency modulation effects...
#                        ##freq_mod_fx = ...
#                        ##update_incrementer = True
#                        begin_period = False
                    
#                    # apply envelope
#                    if use_envelope:
#                        if env_counter == env_td:
#                            # check for sustain symbol
#                            if env[env_index] != ':':
#                                vol_mod_env = float(env[env_index])
#                                env_index += 1
#                                env_counter = 1
#                            else:
#                                # if we're at the first symbol increment the index and proceed as normal
#                                if env_index == env_sustain_index:
#                                    env_index += 1
#                                    vol_mod_env = float(env[env_index])
#                                    env_index += 1
#                                    env_counter = 1
#                                # if we're at the second index, go back to the beginning of the sustain section
#                                else:
#                                    env_index = env_sustain_index + 1
#                                    vol_mod_env = float(env[env_index])
#                                    env_index += 1
#                                    env_counter = 1
#                                    
#                            if env_index == len(env):
#                                # end of envelop reached
#                                # if we have a release, then we're done
#                                if has_release:
#                                    done = True
#                                # if not, sustain the last envelope modulation value
#                                else:
#                                    env_counter = env_td + 1
#                                
#                        else:
#                            env_counter += 1

#                    if use_release:
#                        release_samples += 1

#                    # apply pitchtable
#                    if use_pitchtable:
#                        if pitch_counter == pitch_td:
#                            # check for sustain symbol
#                            if pitch[pitch_index] != ':':
#                                freq_mod_pt = float(pitch[pitch_index])
#                                pitch_index += 1
#                                pitch_counter = 1
#                                update_incrementer = True
#                            else:
#                                # if we're at the first symbol increment the index and proceed as normal
#                                if pitch_index == pitch_sustain_index:
#                                    pitch_index += 1
#                                    freq_mod_pt = float(pitch[pitch_index])
#                                    pitch_index += 1
#                                    pitch_counter = 1
#                                    update_incrementer = True
#                                # if we're at the second index, go back to the beginning of the sustain section
#                                else:
#                                    pitch_index = pitch_sustain_index + 1
#                                    freq_mod_pt = float(pitch[pitch_index])
#                                    pitch_index += 1
#                                    pitch_counter = 1
#                                    update_incrementer = True
#                                    
#                            if pitch_index == len(env):
#                                # end of pitchtable reached
#                                pitch_counter = pitch_td + 1
#                                
#                        else:
#                            pitch_counter += 1

#                    # calculate new incrementer if necessary
#                    if update_incrementer:
#                        incrementer = wavelength * (base_freq * freq_mod_fx * freq_mod_pt) / self._sample_rate
#                        #if incrementer < 1:
#                        #    incrementer = 1
#                        update_incrementer = False

#                        begin_period = True

#                        if not has_release:
#                            done = True
#                        else:
#                            use_release = True
#                            # look for start of release section
#                            for j in range(env_sustain_index + 1, len(env)):
#                                if env[j] == ':':
#                                    end_sus_index = j
#                                    break
#                            # find value in release section less than or equal to current modulation value
#                            for j in range(end_sus_index + 1, len(env)):
#                                if float(env[j]) <= vol_mod_env:
#                                    env_index = j
#                                    break

#                    elif i > duration:
#                        release_samples += 1
#                        for vfx in inst._vfx:
#                            if vfx._release:
#                                ## if index == length of table --> we're at the end of the release for that envelope
#                                ## note ends when the first envelope reaches the end of its release since it ~should~ end at zero
#                                ## the one assumption of this module is that releases are monotonically decreasing functions that end at 0

#                ##### TEMP #####
#                if base_volume == 0:
#                    base_volume = inst._volume
#                if base_freq == 0:
#                    base_volume = 0
#                ##### TEMP #####

#    def butter_lowpass_filter(self, data, cutoff, fs, order=5):
#        b, a = self.butter_lowpass(cutoff, fs, order=order)
#        y = lfilter(b, a, data)
#        return y 
#       
#    def butter_lowpass(self, cutoff, fs, order=5):
#        nyq = 0.5 * fs
#        normal_cutoff = cutoff / nyq
#        b, a = butter(order, normal_cutoff, btype='low', analog=False)
#        return b, a
#
#    def lpf(self, track):
#        z = array.array('h')
#       # Filter requirements.
#        order = 5
#        fs = self._sample_rate       # sample rate, Hz
#        cutoff = 20000  # desired cutoff frequency of the filter, Hz
#        y = self.butter_lowpass_filter(track, cutoff, fs, order)
#        for x in y:
#           z.append(int(x))
#        return z

#    # debugging
#    def output(self):
#        print('Name: ' + self._name)
#        print('Resolution: ' + str(self._resolution))
#        print('Sample Rate: ' + str(self._sample_rate))
#        print('BPM: ' + str(self._bpm))
#        print('Song File: ' + self._song_file_path)
#        print('Number of Instruments: ' + str(len(self._instruments)))
#        print('')
#        n = 1
#       for instrument in self._instruments:
#            print('Instrument' + str(n) + ':')
#            print('Name: ' + instrument._name)
#            print('Volume: ' + str(instrument._volume))
#            print('Wavetable: ' + instrument._wavetable_path)
#            #print('Envelope: ' + instrument._envelope_path)
#            #print('Pitchtable: ' + instrument._pitchtable_path)
#            print('')
#            n += 1