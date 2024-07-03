def mean(points):
    return sum(points) / float(len(points))


def variance(points, m):
    point_variances = {(x - m) ** 2 for x in points}
    return sum(point_variances)


def covariance(points, m):
    """Returns the covariance of a list of complex points."""
    covar = 0.0
    for point in points:
        covar += (point.real - m.real) * (point.imag - m.imag)
    return covar


def determination(points, y_mean, b0, b1) -> float:
    """Calculates the coefficient of determination (R**2) for list of complex points
    and a linear equation."""
    sse = []
    sst = []
    for point in points:
        y_hat = b0 + (b1 * point.real)
        diff = point.imag - y_hat
        sse.append(diff**2)
        diff = point.imag - y_mean
        sst.append(diff**2)
    if sum(sst) == 0:
        return 1  # Horizontal line
    return 1 - (sum(sse) / sum(sst))


def coefficients(points: list) -> list[float]:
    """Calculates the coefficients of a lin. eq. and R**2 for a list of complex points.

    Returns a list of floats [b0, b1, r2]"""
    x = [point.real for point in points]
    m = mean(points)
    var = variance(x, m.real)
    if var > 0:
        b1 = covariance(points, m) / var
        b0 = m.imag - b1 * m.real
        r2 = determination(points, m.imag, b0, b1)
        return [b0, b1, r2]
    return [0, 0, 1]  # Vertical line
