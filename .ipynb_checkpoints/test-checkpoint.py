{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "20316a4d",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "HAPI version: 1.2.2.2\n",
      "To get the most up-to-date version please check http://hitran.org/hapi\n",
      "ATTENTION: Python versions of partition sums from TIPS-2021 are now available in HAPI code\n",
      "\n",
      "           MIT license: Copyright 2021 HITRAN team, see more at http://hitran.org. \n",
      "\n",
      "           If you use HAPI in your research or software development,\n",
      "           please cite it using the following reference:\n",
      "           R.V. Kochanov, I.E. Gordon, L.S. Rothman, P. Wcislo, C. Hill, J.S. Wilzewski,\n",
      "           HITRAN Application Programming Interface (HAPI): A comprehensive approach\n",
      "           to working with spectroscopic data, J. Quant. Spectrosc. Radiat. Transfer 177, 15-30 (2016)\n",
      "           DOI: 10.1016/j.jqsrt.2016.03.005\n",
      "\n",
      "           ATTENTION: This is the core version of the HITRAN Application Programming Interface.\n",
      "                      For more efficient implementation of the absorption coefficient routine, \n",
      "                      as well as for new profiles, parameters and other functional,\n",
      "                      please consider using HAPI2 extension library.\n",
      "                      HAPI2 package is available at http://github.com/hitranonline/hapi2\n",
      "\n"
     ]
    }
   ],
   "source": [
    "from hapi import*"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "4508e268",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Using data\n",
      "\n"
     ]
    }
   ],
   "source": [
    "db_begin('data')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 37,
   "id": "0b138da6",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "Data is fetched from http://hitran.org\n",
      "\n",
      "BEGIN DOWNLOAD: CO2\n",
      "  65536 bytes written to data/CO2.data\n",
      "Header written to data/CO2.header\n",
      "END DOWNLOAD\n",
      "                     Lines parsed: 129\n",
      "PROCESSED\n"
     ]
    }
   ],
   "source": [
    "fetch('CO2',2,1,691.37,692.7)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "77574352",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "dict_keys(['sampletab', 'H2O'])"
      ]
     },
     "execution_count": 4,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "tableList()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "701e2f14",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "-----------------------------------------\n",
      "H2O summary:\n",
      "-----------------------------------------\n",
      "Comment: \n",
      "Contains lines for H2(16O)\n",
      " in 1960.000-2020.000 wavenumber range\n",
      "Number of rows: 528\n",
      "Table type: column-fixed\n",
      "-----------------------------------------\n",
      "            PAR_NAME           PAR_FORMAT\n",
      "\n",
      "            molec_id                  %2d\n",
      "        local_iso_id                  %1d\n",
      "                  nu               %12.6f\n",
      "                  sw               %10.3E\n",
      "                   a               %10.3E\n",
      "           gamma_air                %5.4f\n",
      "          gamma_self                %5.3f\n",
      "              elower               %10.4f\n",
      "               n_air                %4.2f\n",
      "           delta_air                %8.6f\n",
      " global_upper_quanta                 %15s\n",
      " global_lower_quanta                 %15s\n",
      "  local_upper_quanta                 %15s\n",
      "  local_lower_quanta                 %15s\n",
      "                ierr                  %6s\n",
      "                iref                 %12s\n",
      "    line_mixing_flag                  %1s\n",
      "                  gp                %7.1f\n",
      "                 gpp                %7.1f\n",
      "-----------------------------------------\n"
     ]
    }
   ],
   "source": [
    "describeTable('H2O')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 38,
   "id": "8bff9742",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0.9842043"
      ]
     },
     "execution_count": 38,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "mol_id=2\n",
    "iso_id=1\n",
    "abundance(mol_id,iso_id)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 39,
   "id": "83d18ea8",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "{'self': 1.0}\n",
      "0.055120 seconds elapsed for abscoef; nlines = 129\n"
     ]
    }
   ],
   "source": [
    "nu,coef = absorptionCoefficient_Lorentz(SourceTables='CO2', Environment={'T':217.,'p':0.100666}, Diluent={'self':1.0}, WavenumberStep=0.001, HITRAN_units=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 41,
   "id": "cc7f4102",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "2.0240608269181562e-18\n"
     ]
    }
   ],
   "source": [
    "print(max(coef))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 40,
   "id": "b4a556a7",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 640x480 with 1 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "import matplotlib.pyplot as plt\n",
    "fig, ax = plt.subplots()\n",
    "ax.semilogy(nu,coef)\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "055c5af9",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.13"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
