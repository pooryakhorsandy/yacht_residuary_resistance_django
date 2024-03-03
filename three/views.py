#views.py
import pickle
import numpy as np
import pandas as pd
from django.shortcuts import render, redirect
from .forms import RrParametersForm
from math import log,sqrt


def load_model(model_path):
    with open(model_path, 'rb') as model_file:
        return pickle.load(model_file)


def Friction_Resistance(Froude_numbers, S, L):
    g = 9.81
    p = 1025
    v = Froude_numbers * (L * g) ** 0.5
    Rn = v * L / (10 ** (-6))
    Cf = 0.057 / (log(Rn) - 2) ** 2
    Rf = 0.5 * p * (v ** 2) * S * Cf
    return Rf


def Rr_3_parameters(request):
    if request.method == 'POST':
        form = RrParametersForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            L = cleaned_data['L']
            B = cleaned_data['B']
            T = cleaned_data['T']
            D = T + 1.15
            Bmax = 1.18 * B - 0.05
            Froude_numbers = [0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 0.325, 0.35, 0.375, 0.4, 0.425, 0.45]
            results = []

            displacement_model = load_model(r'gradient_boosting_model_B_T_to_div.pkl')
            input_data = np.array([B, T])
            input_data_2d = input_data.reshape(1, -1)
            displacement = displacement_model.predict(input_data_2d)


            S=(1.97 + 0.171 * (B / T)) * sqrt(displacement[0]*L)

            Ax = -3.0330 + -0.0252 * S + 1.6418 * D + 0.5131 * B + 0.0534*displacement[0]

            Ay = -4.9878 + 0.8215 * S + -4.9025 * Ax + 3.4815 * B + 0.3158*displacement[0]

            Pc_model = load_model(r'decision_tree_model_CP.pkl')
            input_data = np.array([Ax, Ay, S, T, B, L])
            input_data_2d = input_data.reshape(1, -1)
            Pc = Pc_model.predict(input_data_2d)

            Lcb_model = load_model(r'decision_tree_regression_model_lcb_to_Ax_Ay_S_D_Bwl_Lwl_Pc.pkl')
            input_data = np.array([Ax, Ay, S, D, B, L, Pc[0]])
            input_data_2d = input_data.reshape(1, -1)
            Lcb = Lcb_model.predict(input_data_2d)

            KMc=0.664 * T + 0.111 * (B ** 2) / T

            IT = -27.1945 + 5.3954 * B + 1.0158 * Ay + 0.5732 * KMc

            IL = -8.6839 + 11.4337 * Ay + 0.1161 * S + -0.3348 * IT + -39.6707 * B

            BM = IT / displacement[0]

            BmL = IL / displacement[0]

            KM = 0.6264 + 0.6891 * KMc + -0.0185 * Ay + -0.0970 * B + 0.0396 * IT

            KB = KM - BM

            KBc = KMc - BmL

            LCF= 0.64 *Lcb[0] -1.84

            CB = displacement[0] / (L * B * D)

            Cwp = Ay / (L * B)

            CM = CB / Pc[0]

            AM = CM * B * T

            LBP = displacement[0] / (AM * Pc[0])

            Cvp = displacement[0] / Ay * T






            Xgb_model = load_model(r'xgb_model.pkl')
            for f in Froude_numbers:
                input_data = np.array([Lcb[0], Pc[0], L / displacement[0] ** (1 / 3), B / T, L / B,f])
                input_data_2d = input_data.reshape(1, -1)
                Rr = Xgb_model.predict(input_data_2d)
                friction_resistance = Friction_Resistance(f, S, L)
                results.append([f, Rr[0], friction_resistance, Rr[0] + friction_resistance])

            # Convert the list of results to a DataFrame
            results_df = pd.DataFrame(results, columns=['Froude Numbers', 'Residuary Resistance', 'Friction Resistance', 'Total Resistance'])

            # Set main_form_parameters in the session
            request.session['main_form_parameters1'] = [Lcb[0], Pc[0], L / displacement[0] ** (1 / 3), B / T, L / B]
            request.session['main_form_parameters2']=[L,Bmax,B,T,D,displacement[0],S,Ax,Ay,LBP]
            request.session['stability']=[KMc,IT,IL,BM,BmL,KM,KB,KBc,LCF]
            request.session['coefficients']=[CB,CM,Cwp,Cvp,Pc[0],AM]


            # Convert results_df to a list for JSON serialization
            results_list = results_df.values.tolist()

            # Render the template with the results as a list
            return render(request, 'result.html', {'results': results_list, 'main_form_parameters1': request.session.get('main_form_parameters1'),'main_form_parameters2': request.session.get('main_form_parameters2'),'stability':request.session.get('stability'),'coefficients':request.session.get('coefficients')})


    else:
        form = RrParametersForm()
    return render(request, 'index.html', {'form': form})


def main_form_parameters(request):
    # Retrieve the main form parameters from the session
    main_form_parameters1 = request.session.get('main_form_parameters1', None)
    main_form_parameters2 = request.session.get('main_form_parameters2', None)

    if main_form_parameters1 is not None:
        return render(request, 'main_form_parameters.html', {'main_form_parameters1': main_form_parameters1, 'main_form_parameters2': main_form_parameters2})
    else:
        # Redirect to the Rr_3_parameters page if main form parameters are not available
        return redirect('Rr_3_parameters')

def stability_coefficients(request):
    stability=request.session.get('stability', None)
    coefficients=request.session.get('coefficients',None)

    if stability is not None:
        return render(request, 'stability_coefficients.html', {'stability': stability, 'coefficients': coefficients})
    else:
        # Redirect to the Rr_3_parameters page if main form parameters are not available
        return redirect('Rr_3_parameters')
