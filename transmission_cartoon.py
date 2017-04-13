import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import wav2rgb
from matplotlib import rc
from pylab import *
from astropy.convolution import Gaussian1DKernel, convolve
import matplotlib.animation as manimation

FFMpegWriter = manimation.writers['ffmpeg']
metadata = dict(title='Transmission spectrum movie', artist='Matplotlib')
writer = FFMpegWriter(fps=15, bitrate = 5000, metadata=metadata)

rcParams['axes.linewidth'] = 2.0
rcParams.update({'font.size':20})
rc('font',**{'family':'serif','serif':['Times']})
#rc('text', usetex=True)


def RGBtoHTML(rgb_tuple):
    """ convert an (R, G, B) tuple to #RRGGBB """
    hexcolor = '#%02x%02x%02x' % rgb_tuple
    return hexcolor


#reads in and smooths water model
model = np.genfromtxt("100H2O.dat")
w, rprs2 = model[:,0], model[:,1]

g = Gaussian1DKernel(stddev=2)
rprs2 = convolve(rprs2, g, boundary = 'extend')		
mindepth, maxdepth = np.min(rprs2), np.max(rprs2)
mindepth -= 0.01*mindepth
wavemin, wavemax = np.min(w), np.max(w)

nframes = 350 
waves = np.linspace(w[0], w[-1], nframes)

fig = plt.figure(figsize = (12,6))

with writer.saving(fig, "transmission_cartoon.mp4", 100):
	for i in range(0,len(waves)):
		gs = gridspec.GridSpec(10,2, width_ratios = [1,1])
		ax1 = plt.subplot(gs[:,0])
		RGB = wav2rgb.wav2RGB((0.4+0.35*(waves[i]-wavemin)/(wavemax-wavemin))*1000)
		circ_color = RGBtoHTML(tuple(RGB))
		depth = np.interp(waves[i], w, rprs2)
		rprs = np.sqrt(depth)

		opac = 0.8*(depth - mindepth)/(maxdepth-mindepth)

		circ_bg = plt.Circle((-0.0,0.0), radius = 1.0, color=circ_color,zorder=2)
		circ_med = plt.Circle((0.7,0.), radius = .1*(1.0+10.0*rprs), color="k",alpha=opac,zorder=3)
		circ_sm = plt.Circle((0.7,0.), radius = .1, color="black",zorder=4)
		ax1.add_patch(circ_bg)
		ax1.add_patch(circ_med)
		ax1.add_patch(circ_sm)
		plt.ylim((-0.5, 0.7))
		plt.xlim((-0.1, 1.1))
		ax1.xaxis.set_visible(False)
		ax1.yaxis.set_visible(False)

		plt.annotate("star", (0.62,0.46), (0.28,0.53),xycoords='data', bbox=dict(boxstyle="round4",fc="w"),arrowprops=dict(arrowstyle='fancy',fc="w",connectionstyle='arc3,rad=-0.2'), annotation_clip=False)
		plt.annotate("planet atmosphere",(0.512,0.1),(0.03,0.3), xycoords='data', bbox=dict(boxstyle="round4",fc="w"),arrowprops=dict(arrowstyle='fancy',fc="w",connectionstyle='arc3,rad=-0.2'), annotation_clip=False)
		plt.annotate("planet core",(0.605,-0.018),(0.06,0.07),xycoords='data', bbox=dict(boxstyle="round4",fc="w"),arrowprops=dict(arrowstyle='fancy',fc="w",connectionstyle='arc3,rad=-0.2'), annotation_clip=False)


		ax2 = plt.subplot(gs[0:9,1])
		plt.plot(w, rprs2, color="k", lw=2)
		plt.xlim((wavemin,wavemax))
		plt.ylim((0.01315, 0.01425))
		plt.ylabel("Fraction of starlight blocked",labelpad=15)
		ax2.axes.get_yaxis().set_ticks([])
		ax2.axes.get_xaxis().set_ticks([])
		vlines(waves[i], 0.01315, 0.01425, color="red",lw=2)
		ax2.annotate('', (1.6,0.01308), (1.2, 0.01308),xycoords='data', arrowprops=dict(arrowstyle='fancy,tail_width=0.3',fc='1.0',ec='0.2'), annotation_clip=False)
		ax2.annotate('', (1.055, 0.01429), (1.055, 0.01420),xycoords='data', arrowprops=dict(arrowstyle='fancy,tail_width=0.3', fc='1.0',ec='0.2'), annotation_clip=False)

		plt.figtext(0.55, 0.08, 'Blue', color="blue")
		plt.figtext(0.92, 0.08, 'Red', color="red")
		plt.figtext(0.7, 0.83, 'Water vapor model')
	
		plt.figtext(0.88, 0.02, "L. Kreidberg", color = '0.5', fontsize=16)

		plt.tight_layout()
		print "Frame #:", i
		writer.grab_frame()
		plt.clf()
