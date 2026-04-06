def late_fusion(p_clinical, p_retinal,
                method="weighted",
                w1=0.5, w2=0.5):

    if method == "weighted":
        return (w1 * p_clinical) + (w2 * p_retinal)

    elif method == "average":
        return (p_clinical + p_retinal) / 2

    elif method == "max":
        return max(p_clinical, p_retinal)

    else:
        raise ValueError("Invalid fusion method")
