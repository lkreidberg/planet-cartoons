import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rc
from pylab import *
import matplotlib.animation as manimation
import batman

FFMpegWriter = manimation.writers['ffmpeg']
metadata = dict(title='Phase curve movie', artist='Matplotlib',
        comment='Shows a phase curve!')
writer = FFMpegWriter(fps=15, metadata=metadata)

rcParams['figure.facecolor'] = 'black'
rcParams['savefig.facecolor'] = 'black'
rc('font',**{'family':'sans-serif','sans-serif':['Arial']})


def get_cartesian_coords(longitude, lat):
	long0 = np.pi/2.
	lat0 = 0.
	R = 0.5
	x = R*np.cos(lat)*np.sin(longitude - long0)
	y = R*(np.cos(lat0)*np.sin(lat) - np.sin(lat0)*np.cos(lat)*np.cos(longitude - long0))
	
	cos_c = np.sin(lat0)*np.sin(lat) + np.cos(lat0)*np.cos(lat)*np.cos(longitude - long0)

	return [x,y]

def model_lc(t):
	params = batman.TransitParams()
	params.t0 = 0 
	params.t_secondary = np.pi 
	params.per = 2.*np.pi				#orbital period
	params.rp = 0.17				#planet radius (in stellar radii)
	params.a = 4.872				#semi-major axis (in stellar radii)
	params.inc = 90.				#orbital inclination
	params.ecc = 0.					#eccentricity
	params.w = 90.					#longitude of periastron  
	params.u = [0.1, 0.3]				#limb darkening coefficients
	params.limb_dark = "quadratic"			#limb darkening model
	params.fp = 1.3e-2				#planet/star flux

	#calculates transit and eclipse models (offset in time for artistic license)
	m_transit = batman.TransitModel(params, t-np.pi/2.)
	m_eclipse = batman.TransitModel(params, t-np.pi/2., transittype="secondary")
	pc = -0.009*np.sin(t)+1.

	lc = m_transit.light_curve(params)*m_eclipse.light_curve(params)*pc		
	return lc

nframes = 400
ngrid = 100
font_color = 'white'

fig = plt.figure(figsize = (10,10))
with writer.saving(fig, "emission_cartoon.mp4", 100):
	for i in range(nframes):
		ax= plt.gca()
		ax.set_axis_off()

		
		phase = float(i)/nframes
		theta = phase*np.pi*2.

		#calculates which longitudes are dark vs. bright
		if (theta< np.pi/2.)&(theta>=0.): 
			quad = 0
			la_bright =  np.pi/2. + theta
			lo_dark = np.linspace(0, la_bright, ngrid)
			lo_bright = np.linspace(la_bright, np.pi, ngrid)
		if (theta>=np.pi/2.)&(theta<3.*np.pi/2.):
			quad = 1
			la_bright = theta - np.pi/2.
			lo_bright = np.linspace(0, la_bright, ngrid)
			lo_dark = np.linspace(la_bright, np.pi, ngrid)
		if (theta>=3.*np.pi/2.)&(theta < 2*np.pi):
			quad = 3
			la_bright = theta - 3.*np.pi/2. 
			lo_dark = np.linspace(0, la_bright, ngrid)
			lo_bright = np.linspace(la_bright, np.pi, ngrid)
			
		#physical coordinates (assuming stellar radius is 1). chosen just to make figure look nice
		ars = 5.5
		per = 19.5
		d = ars*np.cos(theta)

		#converts la,lo to x,y
		la = np.linspace(-np.pi/2., np.pi/2., ngrid)

		a1,b1 = meshgrid(lo_dark, la, sparse = True)
		x_dark,y_dark = get_cartesian_coords(a1,b1)

		a2,b2 = meshgrid(lo_bright, la, sparse = True)
		x_bright,y_bright = get_cartesian_coords(a2,b2)
		
		#plots planet 
		plt.plot(x_dark-d, y_dark,marker = 'o', color='#332a24', markeredgewidth=0., ms=1)
		plt.plot(x_bright-d, y_bright,'#F29807', marker='o', markeredgewidth=0, ms = 1)

		#plots central star
		if theta < np.pi: plt.plot(0,0, marker= 'o', color = 'yellow', ms= 100, markeredgewidth=0., zorder = -1)
		else: plt.plot(0,0, marker= 'o', color = 'yellow', ms= 100, markeredgewidth=0., zorder = 10)

		plt.xlim((-6,6))
		plt.ylim((-6,6))
		
		#plots light curve
		ax_bright = fig.add_axes([0.1,0.15,0.8,0.22])

		t = np.linspace(0, 2.*np.pi, nframes) 
		lc = model_lc(t)

		plt.plot(t, lc, color=font_color, linewidth=3.)
		plt.plot(t[i], lc[i], marker='o', color="#01a9db", ms=15, markeredgewidth=2.)

		time = str(int(phase*per)) + " hours"
		if len(str(int(phase*per)))==1: time = "0" + time
		ax.text(4., 1.4, time, color= font_color, zorder=100, fontsize = 24)
		ax.text(-1., -5.5, "Time", color= font_color, zorder=100, fontsize = 16)
		ax.text(-7.0, -3.5, "Brightness", color= font_color, zorder=100, fontsize = 16, rotation= 90)

		ax.annotate("", (-0.063,0.35), (-0.063,0.27), xycoords ='axes fraction', arrowprops=dict(arrowstyle="-|>",color=font_color, linewidth=2.), size=20)

		ax.text(5., -6, "L. Kreidberg", color = '0.2', zorder = 100, fontsize = 16)

		plt.ylim(0.965, 1.025)
		plt.xlim(-0.1, np.pi*2+0.1)
		ax= plt.gca()
		ax.set_axis_off()

	
		print "Frame #:", i
		writer.grab_frame()
		plt.clf()
