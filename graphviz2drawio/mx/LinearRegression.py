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


def determination(points, y_mean, b0, b1):
    """Returns the coefficient of determination (R**2) for linear equation and list of complex points."""
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
    else:
        return 1 - (sum(sse) / sum(sst))


def coefficients(points):
    """Returns the coefficients of a linear equation and R**2 as a list for a list of complex points."""
    x = [point.real for point in points]
    m = mean(points)
    var = variance(x, m.real)
    if var > 0:
        b1 = covariance(points, m) / var
        b0 = m.imag - b1 * m.real
        r2 = determination(points, m.imag, b0, b1)
        return [b0, b1, r2]
    else:
        return [0, 0, 1]  # Vertical line
